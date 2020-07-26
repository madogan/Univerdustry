"""Download `fasttext` vectors by language.

Example:
    $ python download_vec.py en tr ar ...

"""

import os
import sys


if __name__ == "__main__":
    try:
        for lang in sys.argv[1:]:
            os.system(
                f'wget https://dl.fbaipublicfiles.com/arrival/vectors/wiki.multi.{lang}.vec'
            )
    except IndexError:
        print("You need to pass lang as argument like en,tr")
        exit()
