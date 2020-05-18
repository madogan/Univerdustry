import os
import sys


try:
    for lang in sys.argv[1:]:
        os.system(
            f'wget https://dl.fbaipublicfiles.com/arrival/vectors/wiki.multi.{lang}.vec'
        )
except IndexError:
    print("You need to pass lang as argument like en,tr")
    exit()
