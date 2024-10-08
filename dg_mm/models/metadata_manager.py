"""ユーザーからのアクセスが行われるクラスを記載したモジュールです。"""

from logging import getLogger

from dg_mm.models.base import BaseMapping
from dg_mm.models.grdm import GrdmMapping
from dg_mm.exceptions import StorageNameError

logger = getLogger(__name__)

class MetadataManger():
    """メタデータの管理を行うクラスです。

    Attributes:
        class:
            _ACTIVE_STORAGES(dict):利用可能なストレージの一覧

    """
    _ACTIVE_STORAGES = {"GRDM": "GrdmMapping"}

    def get_metadata(self, schema: str, storage: str, token: str = None, id: str = None, option: list = None) -> dict:
        """引数で指定されたストレージからスキーマの定義に則ったメタデータを取得するメソッドです。

        Args:
            schema (str): スキーマの名称
            storage (str): ストレージの名称
            token (str, optional): ストレージの認証情報。 デフォルトはNone。
            id (str, optional): ストレージを特定する情報。 デフォルトはNone.
            option (list, optional): スキーマの一部のキー。デフォルトはNone.

        Returns:
            dict: マッピングしたメタデータ
        """
        if storage not in MetadataManger._ACTIVE_STORAGES:
            raise StorageNameError("対応していないストレージが指定されました")
        mapping_cls : BaseMapping = globals()[MetadataManger._ACTIVE_STORAGES[storage]]
        instance = mapping_cls()
        param = (schema, token, id, option)
        return instance.mapping_metadata(*param)
