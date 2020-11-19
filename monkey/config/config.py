import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    MONGODB = dict(
        MONGO_HOST = os.getenv('MONGO_HOST',""),
        MONGO_PORT = int(os.getenv('MONGO_PORT','27017')),
        MONGO_USERNAME = os.getenv('MONGO_USERNAME',"monkeyuser"),
        MONGO_PASSWORD = os.getenv('MIONGO_PASSWORD',"monkey123456"),
        DATABASE = 'monkey',
    )