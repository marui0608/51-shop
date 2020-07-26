import os


class Config:
    SECRET_KEY = 'mrsoft'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        '''初始化配置文件'''
        pass


# the config for development
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:542858zry@39.98.192.225:3306/shop'
    DEBUG = True


# define the config
config = {
    'default': DevelopmentConfig
}
