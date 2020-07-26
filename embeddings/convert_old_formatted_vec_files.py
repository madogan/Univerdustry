# -*- coding: utf-8 -*-
"""Convert standard `.vec` file format for our format.

List files same directory with this script and look files
ends with `.vec` and convert to format. Finally save
by changing name of files as starts with `formatted_` .
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join('../vectorizer')))

# FIXME: Find a way to ignore `unresolved-import` warning for vscode.
# This works because we are changing the working directory with above code.
# So it is better to ignore below statement for `unresolved-import` error
# for clean user experience.
from application.word_vec_file import WordVecFile


if __name__ == "__main__":
    model_names = os.listdir(".")

    for model_name in model_names:
        if model_name.endswith(".vec") and not model_name.startswith("formatted_"):
            if WordVecFile.check_is_file_formatted(model_name) is not True:
                WordVecFile.convert_file_format(model_name)
