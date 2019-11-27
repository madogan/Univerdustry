# -*- coding: utf-8 -*-
""""  """

import os


if __name__ == '__main__':
    expose_port = os.getenv("EXPOSE_PORT", None) or 7000
    os.system(f'gunicorn app:app -w 1 --bind 0.0.0.0:{expose_port} --reload --no-sendfile')
