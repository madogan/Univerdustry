from googletrans import Translatordef gdetect(text):    try:        translator = Translator()        lang = translator.detect(text).lang    except Exception:        lang = None    return langdef gtranslate(text, dest_lang):    try:        translator = Translator()        return translator.translate(text, dest_lang).text    except Exception:        return False