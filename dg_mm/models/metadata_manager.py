"""ユーザーからのアクセスが行われるクラスを記載したモジュールです。"""

class MetadataManger():
    """メタデータの管理を行うクラスです。

    Attributes:
        class:
            _ACTIVE_STORAGES(list):利用可能なストレージの一覧

    """

    def get_metadata(self, schema: str, storage: str, token: str = None, project_id: str = None, filter_property: list = None) -> dict:
        """引数で指定されたストレージからスキーマの定義に則ったメタデータを取得するメソッドです。"""
