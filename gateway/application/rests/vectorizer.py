import requests

from application.utils.helpers import get_config


def get_vector(text: str):
    url = get_config("VECTORIZER")
    url += f'/vectorize'

    response = requests.get(
        url=url,
        json={"text": text}
    ).json()

    return response


def lang_detect(text):
    url = get_config("VECTORIZER")
    url += "/detect/lang"

    response = requests.get(
        url=url,
        json={"text": text}
    ).json()

    return response.get("lang", "unknown")


def translate(text, dest_lang):
    url = get_config("VECTORIZER")
    url += "/translate"

    response = requests.get(
        url=url,
        json={"text": text, "dest_lang": dest_lang}
    ).json()

    return response.get("text", None)
