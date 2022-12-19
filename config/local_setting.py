DEBUG = True

# データベース設定
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
    'user': 'test',
    'password': 'test',
    'host': '<接続先ホスト>',
    'db_name': 'dg-mm-db'
})
