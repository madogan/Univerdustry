import io
import os
import logging
import requests

from scholary import scholary
from string import ascii_letters
from pdfminer.pdfpage import PDFPage
from elasticsearch import Elasticsearch
from pdfminer.converter import TextConverter
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from config import DEFAULT_PROFILE_IMAGE_URL, DATABASE_REST_URL, ELASTICSEARCH_URL

from app import logger, celery


es = Elasticsearch(ELASTICSEARCH_URL)


def extract_pdf(url, title):
    pdf_logger = logging.getLogger("pdfminer")
    pdf_logger.setLevel(logging.CRITICAL)
    pdf_logger.disabled = True

    title = "".join([c for c in title if c in (ascii_letters + " ")])
    filename = title.replace(" ", "_").lower()

    logger.info(f'Starting pdf extraction for Publication({filename})')

    dir_name = os.path.join("files")

    raw = requests.get(url).content

    file_path = os.path.join(dir_name, filename + ".pdf")

    with open(file_path, "wb+") as f:
        f.write(raw)

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(file_path, 'rb') as f:
        for page in PDFPage.get_pages(f, caching=True, check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()
        raw = f.read()

    # close open handles
    converter.close()
    fake_file_handle.close()

    return raw, text


@celery.task(bind=True)
def get_author_and_publications(self, author_name):
    """Get author information from scholar and find publications.
    
    It searches from Google Scholar and get publications of the author.
    If eprint url is given, it get pdf of publication and extract text
    from publication. 

    All data sends to Elasticsearch and PostgreSQL Database.

    Arguments:
        author_name: Author information has gotten from scholary.
    """

    query_result = scholary.search_author(author_name)

    try:
        author_info = next(query_result).fill()
    except StopIteration:
        logger.info(f'Author ({author_name}) not found.')
        return False

    if not author_info:
        logger.info(f'Author ({author_name}) not found.')
        return False

    logger.info(f'\nAuthor({author_name}) found.\nAffiliation: {getattr(author_info, "affiliation", None)}')

    # Parse to dictionary as suitable with database columns.
    author = {
        "ident": author_info.id,
        "name": author_info.name,
        "email": getattr(author_info, "email", ""),
        "affiliation": getattr(author_info, "affiliation", ""),
        "cited_by": getattr(author_info, "citedby", 0),
        "cites_per_year": getattr(author_info, "cites_per_year", {}),
        "hindex": getattr(author_info, "hindex", 0),
        "i10index": getattr(author_info, "i10index", 0),
        "interests": getattr(author_info, "interests", []),
        "url_picture": getattr(author_info, "url_picture", DEFAULT_PROFILE_IMAGE_URL)
    }

    # Insert author information.
    response = requests.post(f"{DATABASE_REST_URL}/author", json=author,
                             headers={"Prefer": "resolution=merge-duplicates"})
    logger.info(f'Response for Author({author["name"]}): {response}')

    # Iterate over all publications.
    for pub in author_info.publications:
        logger.info(f'Processing... Publication({pub.bib["title"]})')

        # Check the publication is already exists in database.
        pub_in_db = requests.get(f'{DATABASE_REST_URL}/publication?ident=eq.{pub.id_citations.split(":")[1]}').json()

        # If publication is exists, pass it.
        if len(pub_in_db) > 0:
            logger.info(f'Publication already exists.')
            continue

        # Get details of the publication.
        publication_info = pub.fill()

        # Parse publication as suitable for database.
        publication_dictionary = {
            "ident": publication_info.id_citations.split(":")[1],
            "title": publication_info.bib["title"].replace("\n", " ").replace("\r", " ").replace("\t", " ").strip(),
            "year": publication_info.bib.get("year", None),
            "url": publication_info.bib.get("url", None),
            "source_url": publication_info.bib.get("eprint", None),
            "cited_by": getattr(publication_info, "citedby", 0)
        }

        # If eprint url is found, get and extract PDF.
        if publication_dictionary["source_url"] is not None:
            try:
                raw, text = extract_pdf(publication_dictionary["source_url"], publication_dictionary["title"])
                logger.info(f'Source url is found.')

                publication_dictionary["content_text"] = text.strip().replace("\n", " ").replace("\t", " ")\
                    .replace("\r", " ")
                logger.info(f'Len. Content Text: {len(publication_dictionary.get("content_text", []))}')
            except PDFSyntaxError:
                logger.error(f'While extracting text from pdf there is an error occured. Syntax Error.')

        logger.info(f'Posting data of Publication({publication_dictionary["title"]}) of Author({author["name"]})')

        # Insert publication to database.
        try:
            response = requests.post(f"{DATABASE_REST_URL}/publication",
                                     json=publication_dictionary,
                                     headers={"Prefer": "resolution=merge-duplicates"})
        except requests.exceptions.ConnectionError:
            logger.info(f'We received and error but insertion is correct. We did not solve yet.')

        logger.info(f'Response for Publication({publication_dictionary["title"]}): {response}')
        response = requests.post(f"{DATABASE_REST_URL}/asc_author_publication",
                                 json={"author_id": author["ident"], "publication_id": publication_dictionary["ident"]},
                                 headers={"Prefer": "resolution=merge-duplicates"})

        # Insert to elasticsearch.
        es.index(index="marmara_edu_tr", body={"author": author, "publication": publication_dictionary})
