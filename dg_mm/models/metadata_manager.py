"""ユーザーからのアクセスが行われるクラスを記載したモジュールです。"""

from logging import getLogger

from dg_mm.models.base import BaseMapping
from dg_mm.models.grdm import GrdmMapping
from dg_mm.errors import InvalidStorageError

logger = getLogger(__name__)


class MetadataManager():
    """メタデータの管理を行うクラスです。

    Attributes:
        class:
            _ACTIVE_STORAGES(dict):利用可能なストレージの一覧

    """
    _ACTIVE_STORAGES = {"GRDM": "GrdmMapping"}

    def get_metadata(self, schema: str, storage: str, token: str = None, id: str = None, filter_properties: list = None, project_metadata_id: str = None) -> dict:
        """引数で指定されたストレージからスキーマの定義に則ったメタデータを取得するメソッドです。

        Args:
            schema (str): スキーマの名称
            storage (str): ストレージの名称
            token (str, optional): ストレージの認証情報。 デフォルトはNone。
            id (str, optional): ストレージを特定する情報。 デフォルトはNone.
            filter_properties (list, optional): スキーマの一部のキー。デフォルトはNone.
            project_metadata_id (str, optional): プロジェクトメタデータのid。デフォルトはNone.

        Returns:
            dict: マッピングしたメタデータ
        """
        if storage not in MetadataManager._ACTIVE_STORAGES:
            logger.error(f"ストレージが存在しない({storage})")
            raise InvalidStorageError("対応していないストレージが指定されました。")
        mapping_cls: BaseMapping = globals()[MetadataManager._ACTIVE_STORAGES[storage]]
        instance = mapping_cls()
        param = {
            "schema": schema,
            "token": token,
            "project_id": id,
            "filter_properties": filter_properties,
            "project_metadata_id": project_metadata_id
        }
        return instance.mapping_metadata(**param)
