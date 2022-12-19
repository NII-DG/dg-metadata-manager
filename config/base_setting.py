DEBUG = True

# データベース設定
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
    'user': 'test_user',
    'password': 'test_pw',
    'host': '192.168.196.198:3306',
    'db_name': 'dg_mm_db'
})

SECRET_KEY = 'f9aife8alijdf'

SQLALCHEMY_TRACK_MODIFICATIONS = False
