import requests as rq
from langdetect import detect

from application import logger
from googletrans import Translator
from application.utils.helpers import get_config


def get_vector(text: str, model: str = "fasttext_tr"):
    url = get_config("VECTORIZER")
    url += f'/{model}/vectorize'

    response = rq.get(
        url=url,
        json={"text": text}
    ).json()

    return response


def search(index: str, text: str):
    try:
        real_lang = detect(text)
    except Exception as e:
        logger.error(f'Content lang. detection error: {str(e)}')
        real_lang = "en"

    vector = get_vector(text, real_lang)["vector"]

    langs = get_config("LANGUAGES")

    translator = Translator()

    result = list()
    for lang in langs:
        if lang != real_lang:
            text = translator.translate(text, dest=lang).text

        query_json = {
            "_source": ["title", "url", "authors", "citedby", "year",
                        "lang"],
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "must": [
                                {"multi_match": {
                                    "query": text,
                                    "fields": ["title", "content"]}},
                                {"match": {"content": text}}
                            ],
                            "filter": [{"term": {"lang": lang}}]
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": vector}
                    }
                }
            },
            "highlight": {
                "fragment_size": 100,
                "fields": {
                    "content": {},
                    "title": {}
                }
            },
            "size": 100
        }

        url = get_config("ELASTICSEARCH") + f'/{index}/_search'
        response = rq.get(url, json=query_json).json()
        result += response.get("hits", {}).get("hits", [])

    return result
