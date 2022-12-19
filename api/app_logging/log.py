import datetime
import logging
from logging import getLogger, FileHandler

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
        log_file = f"./logs/app/dg-mm-{today}.log"
        fileHandler = logging.FileHandler(filename=log_file, mode='a', encoding="utf-8")
        fileHandler.setFormatter(formatter)
        l.setLevel(logging.INFO)
        l.addHandler(fileHandler)

        # DBログ
        l = logging.getLogger('sqlalchemy.engine')
        formatter = logging.Formatter('%(asctime)s <%(levelname)s> : %(message)s')
        log_file = f"./logs/db/dg-mm-db-{today}.log"
        fileHandler = logging.FileHandler(filename=log_file, mode='a', encoding="utf-8")
        fileHandler.setFormatter(formatter)
        l.setLevel(logging.INFO)
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
