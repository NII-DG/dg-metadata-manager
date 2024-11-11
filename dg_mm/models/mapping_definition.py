"""マッピング定義を管理するモジュールです。"""

import os
from logging import getLogger

from dg_mm.errors import (
    MappingDefinitionError,
    MappingDefinitionNotFoundError,
    KeyNotFoundError
)
from dg_mm.util import PackageFileReader

logger = getLogger(__name__)


class DefinitionManager():
    """マッピング定義の管理を行うクラスです。"""

    @classmethod
    def get_and_filter_mapping_definition(cls, schema: str, storage: str, filter_properties: list = None) -> dict:
        """マッピング定義の取得と絞り込みを行うメソッドです。

        マッピング定義を取得した後、filter_propertiesに要素が存在する場合はそれを用いて絞り込みを行います。

        Args:
            schema (str): スキーマを一意に定める文字列
            storage (str): ストレージを一意に定める文字列
            filter_properties (list, optional): スキーマの絞り込みに用いるプロパティの一覧。デフォルトはNone

        Returns:
            dict: マッピング定義

        Raises:
            KeyNotFoundError: 引数として渡されたプロパティが存在しない。

        """
        if isinstance(filter_properties, list) and not filter_properties:
            raise KeyNotFoundError("絞り込むプロパティが指定されていません。")

        # マッピング定義ファイルの読み込み
        mapping_definition = cls._read_mapping_definition(schema, storage)

        # 要素が存在する場合のみ絞り込みを行います。
        if filter_properties:
            filtered_definition = {}
            error_keys = []

            sanitized_mapping_keys = {
                k.replace('[]', ''): k for k in mapping_definition.keys()}

            for key in filter_properties:
                matched_keys = [sanitized_mapping_keys[sanitized_key]
                                for sanitized_key in sanitized_mapping_keys if sanitized_key.startswith(key)]

                if matched_keys:
                    for matched_key in matched_keys:
                        filtered_definition[matched_key] = mapping_definition[matched_key]
                else:
                    logger.error(f"プロパティが存在しない({key})")
                    error_keys.append(key)

            if error_keys:
                raise KeyNotFoundError(f"指定したプロパティ: {error_keys} が存在しません。")

            return filtered_definition

        else:
            return mapping_definition

    @classmethod
    def _read_mapping_definition(cls, schema: str, storage: str) -> dict:
        """マッピング定義ファイルの読み取りを行うメソッドです。

        Args:
            schema (str): スキーマを一意に定める文字列
            storage (str): ストレージを一意に定める文字列

        Returns:
            dict: マッピング定義

        Raises:
            MappingDefinitionNotFoundError: マッピング定義ファイルが存在しない

        """
        dir_path = 'data/mapping'
        file_name = f"{storage}_{schema}_mapping.json"

        file_path = os.path.join(dir_path, file_name)

        if not PackageFileReader.is_file(file_path):
            logger.error(f"マッピング定義ファイルが存在しない({file_path})")
            raise MappingDefinitionNotFoundError("マッピング定義ファイルが見つかりません。")

        try:
            mapping_definition = PackageFileReader.read_json(file_path, encoding='utf-8')
        except Exception as e:
            logger.error(f"マッピング定義ファイルの読み込みに失敗({file_path})")
            raise MappingDefinitionError("マッピング定義ファイルの読み込みに失敗しました。") from e

        return mapping_definition
