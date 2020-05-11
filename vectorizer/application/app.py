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

import io
import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel
from fasttext import load_model
from application.utils.helpers import tokenize


def load_vectors(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    _, _ = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = map(float, tokens[1:])
    return data


class VecFile:
    def __init__(self, path):
        self.model = load_vectors(path)

    def get_word_vector(self, word):
        return self.model.get(word, np.zeros(300))


app = FastAPI()

model_fasttext_en = load_model("./embeddings/cc.en.300.bin")
model_fasttext_tr = load_model("./embeddings/cc.tr.300.bin")
model_muse = VecFile("./embeddings/wiki.multi.tr.vec")

models = {"fasttext_tr": model_fasttext_en,
          "fasttext_en": model_fasttext_en,
          "muse": model_muse}


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

        model = models.get(model, models["muse"])

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
