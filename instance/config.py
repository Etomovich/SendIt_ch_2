import os

class Config(object):
    '''This class carries all of courier_app configurations.'''

SECRET_KEY = os.environ.get("SECRET_KEY") or "I_want_to_have_insane_coding_skills_254"

class TestConfiguration(Config):
    DEBUG = True