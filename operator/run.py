import os

if __name__ == '__main__':
    os.system(f'gunicorn app:app -w 1 --bind 0.0.0.0:6000 --reload '
              f'--no-sendfile')
