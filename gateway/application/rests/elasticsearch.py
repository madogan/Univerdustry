import requests as rq
from application.utils.helpers import get_config
from application.rests.vectorizer import lang_detect, get_vector, translate


def search(index: str, text: str):
    src_lang = lang_detect(text)

    langs = get_config("LANGUAGES")

    result = list()
    for lang in langs:
        if lang != src_lang:
            text = translate(text, lang)

        vector = get_vector(text)["vector"]

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
