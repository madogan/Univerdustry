import requests as rq

from application import logger
from application.utils.helpers import get_config
from application.utils.text import preprocess_text
from application.rests.vectorizer import lang_detect, get_vector, translate


def search(index: str, text: str):
    src_lang = lang_detect(text)

    query = preprocess_text(text.strip().lower())

    vector = get_vector(text)["vector"]

    matches = [
        {"match": {"title": query}},
        {"match": {f'title_{src_lang}': query}},
        {"match": {"content": query}},
        {"match": {f'content_{src_lang}': query}},
    ]

    logger.info(f'matches: {matches}')

    query_json = {
        "_source": ["title", "url", "authors", "citedby", "year",
                    "lang"],
        "query": {
            "script_score": {
                "query": {
                    "bool": {
                        "should": [matches]
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

    return response.get("hits", {}).get("hits", [])


def get_docs(ids, projections=None):
    q = {
        "query": {
            "ids": {
                "values": list(ids)
            }
        }
    }

    if projections:
        q["_source"] = projections

    url = get_config("ELASTICSEARCH") + "/_search"
    response = rq.get(url, json=q).json()

    return response.get("hits", {}).get("hits", [])


def update_vector(index, _id, vector, rcoef, relevance):
    logger.info(f'{type(relevance)}: {relevance}')

    sign = "+" if str(relevance).strip().lower() == "true" else "-"

    inline = "for (int i=0; i<ctx._source.vector.length; ++i){ctx._source.vector[i]=(ctx._source.vector[i]" + sign + "(params.vector[i]*params.rcoef))/2}"

    q = {
        "script": {
            "lang": "painless",
            "params": {
                "vector": list(vector),
                "rcoef": rcoef
            },
            "inline": inline
        }
    }

    response = rq.post(get_config("ELASTICSEARCH") + f'/{index}/_update/{_id}',
                       json=q).json()
    logger.info(response)

    return response
