import os


class Config:
    SECRET_KEY = '123456'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        '''初始化配置文件'''
        pass


# the config for development
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:542858zry@39.98.192.225:3306/51-Shop'
    DEBUG = True


# define the config
config = {
    'default': DevelopmentConfig
}

IMG_URL = os.path.join(os.path.dirname(__file__),'app/static/images/goods/')
