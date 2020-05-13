import base64
import os
from _md5 import md5

import requests
from requests.exceptions import SSLError

from application import celery, logger
from application.rests.mongo import update_one, find
from application.utils.decorators import celery_exception_handler
from application.utils.helpers import extract_text_from_pdf, get_config
from application.tasks.find_pdf_secondarily import t_find_pdf_secondarily
from application.tasks.elasticsearch_indexing import t_elasticsearch_indexing


@celery.task(bind=True, name="find_pdf_primarily", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_find_pdf_primarily(self, pub_id: str, title: str, authors: list,
                         url: str):
    resd = {"status": "ok"}

    if url:
        files_path = get_config("FILES_PATH")

        file_name = md5(url.encode("utf-8")).hexdigest()

        if not os.path.exists(files_path):
            os.makedirs(files_path)

        try:
            pdf_raw = requests.get(url).content
        except SSLError:
            pdf_raw = requests.get(url, verify=False).content

        full_path = f'{files_path}{os.path.sep}{file_name}.pdf'

        with open(full_path, "wb+") as f:
            f.write(pdf_raw)

        resd["path"] = full_path

        try:
            content = extract_text_from_pdf(full_path)
        except Exception as e:
            resd["extraction_failure"] = str(e)
            logger.debug(e)
            content = None

        update_one("publication", {
            "filter": {"id": {"$eq": pub_id}},
            "update": {
                "$set": {
                    "raw_base64": base64.encodebytes(pdf_raw).decode("utf-8"),
                    "content": content
                }
            },
            "upsert": True
        })

        if content:
            logger.info(f'Content is added to publication.')
            t_elasticsearch_indexing.apply_async((pub_id,))
    else:
        authors = find("author", {
            "filter": {"id": {"$in": authors}},
            "projection": {"name": 1}
        })
        t_find_pdf_secondarily.apply_async(
            (pub_id, title, [a["name"] for a in authors])
        )

    return resd
