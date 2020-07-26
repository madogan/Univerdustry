# -*- coding: utf-8 -*-
"""Run application using `Gunicorn`_.

.. _Gunicorn:
    http://docs.gunicorn.org/en/stable/
"""

import os


if __name__ == '__main__':
    port = os.getenv("PORT") or 9001
    os.system(f"gunicorn application:app --worker-class eventlet -w 1 "
              f"--bind 0.0.0.0:{port} --reload --no-sendfile "
              f"--timeout 120")
