import os
import base64
import urllib3

from _md5 import md5
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from application import celery, logger
from application.rests.mongo import update_one
from application.utils.decorators import celery_exception_handler
from application.tasks.elasticsearch_indexing import t_elasticsearch_indexing
from application.utils.helpers import (extract_text_from_pdf, get_config,
                                       download)


@celery.task(bind=True, name="find_pdf_secondarily", max_retries=3)
@celery_exception_handler(ConnectionError)
def t_find_pdf_secondarily(self, pub_id: str, title: str, authors: list):
    resd = {"status": "ok"}

    try:
        # Her authoru tek tek kontrol etmemizi sağlayan for döngüsü
        for single_author in authors:
            # author için istek atıyoruz
            http = urllib3.PoolManager()
            response = http.request(
                'GET', 'https://libgen.is/scimag/?q=' + single_author
            )
            html_text = response.data
            soup = BeautifulSoup(html_text, 'html.parser')

            # arama sonucunda data döndü mü onu kontrol ediyoruz
            try:
                total_value = str(
                    soup.find('div', attrs={'style': 'float:left'}).getText()
                ).split(" ")[0]
            except Exception:
                total_value = 0
            # eğer arama sonucunda bir data dönmedi ise diğer yazare
            # geçmesi için continue diyoruz döngüye
            if total_value == 0:
                continue

            # burada sayfa sayısını hesaplıyoruz. double ile bölmede kalan
            # muhabbetlerinden ötürü kontrol yapıp gerekliyse
            # toplam sayfa sayısına bir ekliyoruz en son sayfayı ıskalamamak için
            total_page_dobule = int(total_value) / 25
            total_page = int(int(total_value) / 25)
            if total_page != total_page_dobule:
                total_page += 1

            # Burda bir yazarın sonuçlarını taramak için sayfalarda geziyoruz.
            # İlk sayfa için yukarıda istek atmıştık 0'dan farklı bir sonuç
            # sayısı varsa buraya gelmiştik.
            # bu yüzden ilk sayfa için istek atmıyoruz.
            # eğer ilk sayfada sonuç bulunmazsa ve sayfa sayısı 1'den büyük
            # ise döngünün en sonunda istek atıyor
            # ve döngü yeni sayfanın içinde arama yapacak şekilde devam ediyor
            for i in range(total_page):
                counter = 0
                for row in soup.find_all('tr'):
                    if counter == 0:  # For initial row. Because it contains table information of page
                        counter += 1
                        continue
                    row_item = row.find_all('td')
                    row_title = row_item[1].find_all('a')[0].text
                    ratio = fuzz.ratio(row_title.lower(),
                                       title.lower())  # row title ve verilen title benzer mi diye bakılıyor

                    if ratio > 75:
                        url_for_get = row_item[4].find_all('li')
                        href = url_for_get[1].find_all('a', href=True)[0][
                            'href']
                        response_for_pdf = http.request('GET', href)
                        pdf_page = BeautifulSoup(response_for_pdf.data,
                                                 'html.parser')
                        pdf_url = pdf_page.find_all(
                            'td', {'align': 'center'}
                        )[0].find_all('a', href=True)[0]['href']

                        pdf_raw = download(pdf_url)

                        files_path = get_config("FILES_PATH")

                        if not os.path.exists(files_path):
                            os.makedirs(files_path)

                        file_name = md5(pdf_url.encode("utf-8")).hexdigest()

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
                                    "raw_base64": base64.encodebytes(
                                        pdf_raw).decode("utf-8"),
                                    "content": content
                                }
                            },
                            "upsert": True
                        })

                        if content:
                            logger.info(f'Content is added to publication.')

                            t_elasticsearch_indexing.apply_async((pub_id,))

                            return resd

                if total_page > 1:
                    response = http.request(
                        'GET', 'https://libgen.is/scimag/?q='
                               + single_author + '&page=' + str(i + 2)
                    )
                    html_text = response.data
                    soup = BeautifulSoup(html_text, 'html.parser')
    except Exception as e:
        logger.exception(e)

    t_elasticsearch_indexing.apply_async((pub_id,))

    return resd
