"""マッピングクラスのプロトコルを記載したモジュールです。"""

from typing import Any, Protocol


class BaseMapping(Protocol):
    """マッピングクラスのプロトコルです。

    各ストレージのマッピングクラスに特定のメソッドや属性を持つことを要求します。

    """

    def mapping_metadata(self, schema: str, storage: str, *args: Any, **kwards):
        """スキーマの定義に従いマッピングを行うメソッドです。"""
