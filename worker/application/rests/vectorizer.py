import requests

from application.utils.helpers import get_config


def get_vector(text: str):
    url = get_config("VECTORIZER_REST")
    url += "/vectorize"

    response = requests.get(
        url=url,
        json={"text": text}
    )

    return response.json()
