# -*- coding: utf-8 -*-
""""  """

import os


if __name__ == '__main__':
    os.system(f'gunicorn app:app -w 1 --bind 0.0.0.0:5090 --reload --no-sendfile')
