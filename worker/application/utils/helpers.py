# -*- coding: utf-8 -*-
"""This module consists several necessary function independently."""

import datetime
from string import ascii_lowercase, digits

import pdfplumber
from flask import current_app
from application import logger
from application.utils.contextor import ensure_app_context


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


def get_content_of_pdf(file_path):
    text_of_pages = ""

    pdf = pdfplumber.open(file_path)
    for page in pdf.pages:
        text_of_pages += page.extract_text()
    pdf.close()

    return clean_text(text_of_pages)
