import os
import sys

os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"

# Store path of application root in a variable.
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# Remove default handler.
logger.remove()

# Console logger.
logger.add(sink=sys.stderr, level=os.environ.get("CONSOLE_LOG_LEVEL", "INFO"),
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| "
                  "{message}")

# File logger.
logger.add(sink=os.path.join(ROOT_DIR, "logs", "log_{time}.log"),
           serialize=True,
           rotation="10 MB",  # Every log file max size.
           # Remove logs older than 3 days.
           retention="3 days", level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))


import fasttext
import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel
from application.word_vec_file import WordVecFile
from application.utils.helpers import lang_detect, tokenize, translate

app = FastAPI()

lang_model = fasttext.load_model("../embeddings/lid.176.ftz")

path_model_tr = "../embeddings/formatted_wiki.multi.tr.vec"
path_model_en = "../embeddings/formatted_wiki.multi.en.vec"
path_model_fr = "../embeddings/formatted_wiki.multi.fr.vec"
path_model_de = "../embeddings/formatted_wiki.multi.de.vec"
path_model_ar = "../embeddings/formatted_wiki.multi.ar.vec"

models = {
    "tr": WordVecFile(path_model_tr),
    "en": WordVecFile(path_model_en),
    # "fr": WordVecFile(path_model_fr),
    # "de": WordVecFile(path_model_de),
    # "ar": WordVecFile(path_model_ar),
}


@app.get("/")
def index():
    return {"status": "ok"}


class TextModel(BaseModel):
    text: str = ""


@app.get("/vectorize")
async def get_vector(text_model: TextModel):
    text = text_model.text.strip()
    lang = lang_detect(text)

    try:
        if not text:
            raise ValueError("Empty text!")

        tokens = tokenize(text)

        model = models.get(lang)

        vectors = list()
        for token in tokens:
            vectors.append(list(map(float, model.get_word_vector(token))))

        vector = list(np.mean(vectors, axis=0))
    except Exception as e:
        logger.error(e)
        vector = [0] * 300

    result = {
        "text": text,
        "lang": lang,
        "vector": vector
    }

    return result


@app.get("/detect/lang")
async def detect_lang(text_model: TextModel):
    text = text_model.text.strip()

    if not text:
        raise ValueError("Empty text!")

    return {"lang": lang_detect(text), "status": "ok"}


class TranslationTextModel(BaseModel):
    text: str = ""
    dest_lang: str = "en"


@app.get("/translate")
async def translate_text(params: TranslationTextModel):
    text = params.text.strip()
    dest_lang = params.dest_lang.strip() or "en"

    if not text:
        text = ""
    else:
        text = translate(text, dest_lang)

    return {"text": text, "status": "ok"}
