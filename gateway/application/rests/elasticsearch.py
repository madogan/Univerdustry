import requests as rq
from langdetect import detect

from application import logger
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
        lang = detect(text)
    except Exception as e:
        logger.error(f'Content lang. detection error: {str(e)}')
        lang = "en"

    fasttext = get_vector(text, f'fasttext_{lang}')

    query_json = {
        "query": {
            "script_score": {
                "query": {"match": {"content": text}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'fasttext') + 1.0",
                    "params": {"query_vector": fasttext["vector"]}
                }
            }
        }
    }

    url = get_config("ELASTICSEARCH") + f'/{index}/_search'
    response = rq.get(url, json=query_json).json()

    return response
