# -*- coding: utf-8 -*-
"""Run application using `Gunicorn`_.

.. _Gunicorn:
    http://docs.gunicorn.org/en/stable/
"""

import os


if __name__ == '__main__':
    expose_port = os.getenv("EXPOSE_PORT") or 5090
    os.system(f"gunicorn worker:app --worker-class eventlet -w 1 "
              f"--bind 0.0.0.0:{expose_port} --reload --no-sendfile "
              f"--timeout 120")
