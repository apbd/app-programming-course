class Config:
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://albert:albert@localhost/generalblog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
