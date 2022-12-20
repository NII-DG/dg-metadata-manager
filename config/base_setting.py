DEBUG = True

# [database]
# データベース接続設定
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8'.format(**{
    'user': 'test_user',
    'password': 'test_pw',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'dg_mm_db'
})
SQLALCHEMY_TRACK_MODIFICATIONS = False


# [log] ロギングの設定ファイル
# DB ロギングレベル['DEBUG'|'INFO'|'WARN'|'ERROR']
DB_LOGGING_LEVEL = 'DEBUG'
# DB ログ出力先ディレクトリ
DB_LOGGING_DIR_PATH = "./logs/db/"
# DB ログ出力先ファイル名(指定ファイル名に.logが付与されます。)
DB_LOGGING_FILE_NAME = "dg-mm-db"
# APP ロギングレベル['DEBUG'|'INFO'|'WARN'|'ERROR']
APP_LOGGING_LEVEL = 'DEBUG'
# APP ログ出力先ディレクトリ
APP_LOGGING_DIR_PATH = "./logs/app/"
# APP ログ出力先ファイル名(指定ファイル名に.logが付与されます。)
APP_LOGGING_FILE_NAME = "dg-mm"


SECRET_KEY = 'base'
