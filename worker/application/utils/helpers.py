# -*- coding: utf-8 -*-
"""This module consists several necessary function independently."""

import re
from string import ascii_lowercase, digits

import nltk
import requests
from cleantext import clean
from flask import current_app
from nltk.stem import WordNetLemmatizer

from application import logger
from application.utils.contextor import ensure_app_context

from langdetect import detect


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
        return preprocess_text(text)


def preprocess_text(text):
    cleaned_text = ''
    for line in text.splitlines():  # cleaning - character at the end of lines
        if len(line) > 0:
            if line[-1] == '-':
                line = line[:-1]
            else:
                line += " "
            cleaned_text += line

    document = clean(cleaned_text,
                     fix_unicode=True,  # fix various unicode errors
                     to_ascii=True,
                     # transliterate to closest ASCII representation
                     lower=True,  # lowercase text
                     no_line_breaks=False,
                     # fully strip line breaks as opposed to only normalizing them
                     no_urls=True,  # replace all URLs with a special token
                     no_emails=True,
                     # replace all email addresses with a special token
                     no_phone_numbers=True,
                     # replace all phone numbers with a special token
                     no_numbers=True,
                     # replace all numbers with a special token
                     no_digits=True,  # replace all digits with a special token
                     no_currency_symbols=False,
                     # replace all currency symbols with a special token
                     no_punct=True,  # fully remove punctuation
                     replace_with_url=" ",
                     replace_with_email=" ",
                     replace_with_phone_number=" ",
                     replace_with_number=" ",
                     replace_with_digit=" ",
                     )

    stemmer = WordNetLemmatizer()

    en_stop = set(
        nltk.corpus.stopwords.words('english') + nltk.corpus.stopwords.words(
            'turkish'))

    # Remove all the special characters
    document = re.sub(r'\W', ' ', str(document))

    # remove all single characters
    document = re.sub(r'\s+[a-zA-ZğüşöçıIİĞÜŞÖÇ]\s+', ' ', document)

    # Remove single characters from the start
    document = re.sub(r'\^[a-zA-ZğüşöçıIİĞÜŞÖÇ]\s+', ' ', document)

    # Substituting multiple spaces with single space
    document = re.sub(r'\s+', ' ', document, flags=re.I)

    # Lemmatization
    if detect(document) == 'tr':
        deasciifier = Deasciifier(document)
        tokens = deasciifier.convert_to_turkish().split()
    else:
        tokens = document.split()
        tokens = [stemmer.lemmatize(word) for word in tokens]

    tokens = [word for word in tokens if word not in stop_words]
    tokens = [word for word in tokens if len(word) > 3]

    preprocessed_text = ' '.join(tokens)

    return preprocessed_text
