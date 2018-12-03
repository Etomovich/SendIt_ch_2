import os


class Config(object):
    '''This class carries all of courier_app configurations.'''

    SECRET_KEY = os.environ.get("SECRET_KEY") or "I_want_to_have_insane_coding_skills_254"
    MAIN_URL = os.getenv("DB_URL")

class TestConfiguration(Config):
    DEBUG = True
    TESTING = True
    TEST_URL = os.getenv("TEST_DB_URL")

class MyDatabasebUrl(object):
    CURRENT_URL = Config.MAIN_URL