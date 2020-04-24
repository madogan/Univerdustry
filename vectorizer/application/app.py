import osimport sysos.environ["LC_ALL"] = "C.UTF-8"os.environ["LANG"] = "C.UTF-8"# Store path of application root in a variable.ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")# Import logging library.# More about loguru: https://loguru.readthedocs.io/en/stable/overview.htmlfrom loguru import logger# Remove default handler.logger.remove()# Console logger.logger.add(sink=sys.stderr, level=os.environ.get("CONSOLE_LOG_LEVEL", "INFO"),           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| "                  "{message}")# File logger.logger.add(sink=os.path.join(ROOT_DIR, "logs", "log_{time}.log"),           serialize=True,           rotation="10 MB",  # Every log file max size.           # Remove logs older than 3 days.           retention="3 days", level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))import numpy as npfrom fastapi import FastAPIfrom langdetect import detectfrom pydantic import BaseModelfrom fasttext import load_modelfrom application.utils.helpers import tokenizeapp = FastAPI()model_en = load_model("/embeddings/cc.en.300.bin")model_tr = load_model("/embeddings/cc.tr.300.bin")models = {"tr": model_tr, "en": model_en}@app.get("/")def index():    return {"status": "ok"}class TextItem(BaseModel):    text: str    lang: str = "en"@app.get("/vectorize")async def get_word_vector(ti: TextItem):    ti.text = ti.text.strip()    ti.lang = detect(ti.text)    tokens = tokenize(ti.text)    model = models.get(ti.lang, models["en"])    async def vectorize():        vectors = list()        for token in tokens:            vectors.append(list(map(float, model.get_word_vector(token))))        return list(np.mean(vectors, axis=0))    return {        "text": ti.text,        "vector": await vectorize(),        "lang": ti.lang    }