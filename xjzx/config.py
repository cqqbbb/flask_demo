import redis
import os


class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://name:password@host:port/database'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    # REDIS_DB = 10
    SECRET_KEY = "itheima"
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 七牛云配置
    QINIU_AK = 'H999S3riCJGPiJOity1GsyWufw3IyoMB6goojo5e'
    QINIU_SK = 'uOZfRdFtljIw7b8jr6iTG-cC6wY_-N19466PXUAb'
    QINIU_BUCKET = 'itcast20171104'
    QINIU_URL = 'http://oyvzbpqij.bkt.clouddn.com/'


class DevelopConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost:3306/xjzx10'
    DEBUG = True
