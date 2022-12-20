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
DB_LOGGING_LEVEL = 'INFO'
# DB ログ出力先ディレクトリ
DB_LOGGING_DIR_PATH = "./logs/db/"
# DB ログ出力先ファイル名(指定ファイル名に.logが付与されます。)
DB_LOGGING_FILE_NAME = "dg-mm-db"
# DB ログファイルの最大バイト数(bytes)
DB_LOGGING_MAX_BYTES = 2000
# APP ロギングレベル['DEBUG'|'INFO'|'WARN'|'ERROR']
APP_LOGGING_LEVEL = 'INFO'
# APP ログ出力先ディレクトリ
APP_LOGGING_DIR_PATH = "./logs/app/"
# APP ログ出力先ファイル名(指定ファイル名に.logが付与されます。)
APP_LOGGING_FILE_NAME = "dg-mm"
# APP ログファイルの最大バイト数(bytes)
APP_LOGGING_MAX_BYTES = 2000

SECRET_KEY = 'base'
