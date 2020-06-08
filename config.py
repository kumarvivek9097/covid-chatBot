import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = b'\x81\xa4\xbdb\x7fS:\xe0\x03\xea\xd5\x89;\xbf\xe8\xf9'
