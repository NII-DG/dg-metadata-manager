import datetime
import logging
from logging import getLogger, FileHandler
import logging.handlers
from application import app
import os
from api.utils.enums.log_level import LogLevel

#
# ログクラス
#


class Log:
    # --------------------------
    # コンストラクト
    # --------------------------
    def __init__(self):
        today = datetime.date.today().strftime("%Y-%m-%d")

        # アプリケーションログ
        l = logging.getLogger("app")
        formatter = logging.Formatter('%(asctime)s <%(levelname)s> : %(message)s')
        log_file_path = os.path.join(app.config['APP_LOGGING_DIR_PATH'], app.config['APP_LOGGING_FILE_NAME'])
        log_file = '{file_path}-{date}.log'.format(**{
            'file_path': log_file_path,
            'date': today
        })
        fileHandler = logging.FileHandler(
            filename=log_file,
            mode='a',
            encoding="utf-8",
        )
        # ログローテーションの設定は検証要
        # backup=を設定しないと聞かない
        # fileHandler = logging.handlers.RotatingFileHandler(
        #     filename=log_file,
        #     mode='a',
        #     encoding="utf-8",
        #     maxBytes=app.config['APP_LOGGING_MAX_BYTES'])
        fileHandler.setFormatter(formatter)
        # log leveの設定
        log_level = app.config['APP_LOGGING_LEVEL']
        if LogLevel.DEBUG.name == log_level:
            l.setLevel(logging.DEBUG)
        elif LogLevel.INFO.name == log_level:
            print("APP OK")
            l.setLevel(logging.INFO)
        elif LogLevel.WARN.name == log_level:
            l.setLevel(logging.WARN)
        elif LogLevel.ERROR.name == log_level:
            l.setLevel(logging.ERROR)

        l.addHandler(fileHandler)

        # DBログ
        l = logging.getLogger('sqlalchemy.engine')
        formatter = logging.Formatter('%(asctime)s <%(levelname)s> : %(message)s')
        log_file_path = os.path.join(app.config['DB_LOGGING_DIR_PATH'], app.config['DB_LOGGING_FILE_NAME'])
        log_file = '{file_path}-{date}.log'.format(**{
            'file_path': log_file_path,
            'date': today
        })
        fileHandler = logging.FileHandler(
            filename=log_file,
            mode='a',
            encoding="utf-8",
        )
        # ログローテーションの設定は検証要
        # backup=を設定しないと聞かない
        # fileHandler = logging.handlers.RotatingFileHandler(
        #     filename=log_file,
        #     mode='a',
        #     encoding="utf-8",
        #     maxBytes=app.config['DB_LOGGING_MAX_BYTES'])
        fileHandler.setFormatter(formatter)
        # log leveの設定
        log_level = app.config['DB_LOGGING_LEVEL']
        if LogLevel.DEBUG.name == log_level:
            l.setLevel(logging.DEBUG)
        elif LogLevel.INFO.name == log_level:
            print("DB OK")
            l.setLevel(logging.INFO)
        elif LogLevel.WARN.name == log_level:
            l.setLevel(logging.WARN)
        elif LogLevel.ERROR.name == log_level:
            l.setLevel(logging.ERROR)
        l.addHandler(fileHandler)

    def Info(self, msg):
        """
        Logging Info
        """
        log = logging.getLogger('app')
        log.info(msg)

    def Error(self, msg):
        """
        Logging Error
        """
        log = logging.getLogger('app')
        log.error(msg)

    def Debug(self, msg):
        """
        Logging Debug
        """
        log = logging.getLogger('app')
        log.debug(msg)

    def Warn(self, msg):
        """
        Logging Warn
        """
        log = logging.getLogger('app')
        log.warn(msg)
