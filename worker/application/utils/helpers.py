# -*- coding: utf-8 -*-
"""This module consists several necessary function independently."""

import io
from string import ascii_lowercase, digits

from flask import current_app

from application import logger
from application.utils.contextor import ensure_app_context

import requests

@ensure_app_context
def get_config(name):
    return current_app.config.get(name, None)


@ensure_app_context
def set_config(name, value):
    current_app.config[name] = value


@ensure_app_context
def get_logger():
    return logger


def clean_text(text: str):
    accepted_chars = ascii_lowercase + digits + "_ " + " "

    s1 = " ".join(text.split())
    s2 = "".join([c for c in s1 if c in accepted_chars])
    return s2


def extract_file_name_from_url(url):
    file_name = url.split("/")[-1].split(".")[0].lower().replace(" ", "")
    file_name = clean_text(file_name)
    return file_name


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as fp:
        response = requests.put(get_config("APACHE_TIKA") + "/tika",
                                data=fp.read(),
                                headers={"Content-type": "application/pdf"})
        text = response.text

    if text:
        return text
