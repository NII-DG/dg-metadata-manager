from logging import DEBUG, INFO, config
import datetime


# ファイル名に入れる日付フォーマット
today = datetime.date.today().strftime("%Y-%m-%d")

config.dictConfig(
    {
        "version": 1,
        # ログフォーマット設定
        "formatters": {
            "formatter": {
                "format": "%(levelname)s  %(asctime)s [%(module)s] %(message)s"
            }
        },
        # ハンドラー設定
        "handlers": {
            # 標準出力ハンドラー
            "streamHandler": {
                "class": "logging.StreamHandler",
                "formatter": "formatter",
                "level": INFO
            },
            # ファイル出力ハンドラー
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "formatter",
                "level": DEBUG,
                # ログファイルを出力したい場所のパスとファイル名を指定
                "filename": f"./log/dg-mm-{today}.log",
                "encoding": "utf-8"
            }
        },
        # ロガー設定
        "loggers": {
            "basicLogger": {
                "handlers": [
                    "streamHandler",
                    "fileHandler"
                ],
                "level": INFO,
                "propagate": 0
            }
        }
    }
)
