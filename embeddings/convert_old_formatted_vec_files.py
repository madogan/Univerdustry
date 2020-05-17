import os
import sys
sys.path.append(os.path.abspath(os.path.join('../vectorizer')))

from application.word_vec_file import WordVecFile

model_names = os.listdir(".")

for model_name in model_names:
    if model_name.endswith(".vec") and not model_name.startswith("formatted_"):
        if WordVecFile.check_is_file_formatted(model_name) is not True:
            WordVecFile.convert_file_format(model_name)
