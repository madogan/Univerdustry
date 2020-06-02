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

import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel
from application.utils.helpers import tokenize
from application.word_vec_file import WordVecFile

app = FastAPI()

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


@app.get("/{model}/vectorize")
async def get_vector(model, text_model: TextModel):
    text = text_model.text.strip()

    try:
        if not text:
            raise ValueError("Empty text!")

        tokens = tokenize(text)

        model = models.get(model, models["en"])

        vectors = list()
        for token in tokens:
            vectors.append(list(map(float, model.get_word_vector(token))))

        vector = list(np.mean(vectors, axis=0))
    except Exception as e:
        logger.error(e)
        vector = [0] * 300

    result = {
        "text": text,
        "vector": vector
    }

    return result
