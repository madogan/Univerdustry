import requests as rq

from application.utils.helpers import get_config


def search(index: str, text: str):
    url = get_config("VECTORIZER") + "/vectorize"
    vectorization = rq.get(url, json={"text": text}).json()

    query_json = {
        "query": {
            "script_score": {
                "query": {"match": {"content": text}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'fasttext') + 1.0",
                    "params": {"query_vector": vectorization["vector"]}
                }
            }
        },
        "explain": True
    }

    url = get_config("ELASTICSEARCH") + f'/{index}/_search'
    response = rq.get(url, json=query_json).json()

    return response
