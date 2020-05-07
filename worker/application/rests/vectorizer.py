import requests

from application.utils.helpers import get_config


def get_vector(text: str, model: str = "fasttext_tr"):
    url = get_config("VECTORIZER")
    url += f'/{model}/vectorize'

    response = requests.get(
        url=url,
        json={"text": text}
    ).json()

    return response
