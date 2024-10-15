"""GRDMストレージに関するモジュールです。"""

from typing import Optional
from logging import getLogger

from mapping_definition import DefinitionManager
from dg_mm.exceptions import (
    MappingDefinitionError,
    MetadataTypeError,
    NotFoundKeyError,
    NotFoundSourceError
)

logger = getLogger(__name__)


class GrdmMapping():
    """GRDMとのマッピングを行うクラスです。

    Attributes:
        instance:
            _mapping_definition(dict): マッピング定義
            _new_schema(dict): 作成するスキーマ

    """

    def mapping_metadata(self, schema: str, token: str, project_id: str, filter_properties: list = None) -> dict:
        """スキーマの定義に従いマッピングを行うメソッドです。

        Args:
            schema (str): スキーマを一意に定める文字列
            storage (str): ストレージを一意に定める文字列
            token (str): GRDMの認証に用いるトークン
            project_id (str): GRDMのプロジェクトを一意に定めるID
            filter_properties (list): スキーマの絞り込みに用いるプロパティの一覧。デフォルトはNone

        Returns:
            dict:　スキーマにデータを挿入したもの

        Raises:
            NotFoundSourceError: メタデータ取得先が存在しない
            MappingDefinitionError: マッピング定義の内容に誤りがある

        """
        # GRDMの認証
        grdm_access = GrdmAccess()
        grdm_access.check_authentication(token, project_id)

        if filter_properties is None:
            filter_properties = []

            # マッピング定義の取得
            storage = "GRDM"
            self._mapping_definition = DefinitionManager.get_mapping_definition(
                schema, storage, filter_properties)

        try:
            # メタデータ取得先の特定
            metadata_sources = self._find_metadata_sources()

            # 各データ取得先からデータを取得
            source_data = {}
            if metadata_sources:
                source_mapping = {
                    "project_info": grdm_access.get_project_info,
                    "member_info": grdm_access.get_member_info,
                    "project_metadata": grdm_access.get_project_metadata,
                    "file_metadata": grdm_access.get_file_metadata,
                }
                for source in metadata_sources:
                    if source in source_mapping:
                        source_data[source] = source_mapping[source]()
                    else:
                        raise NotFoundSourceError(f"メタデータ取得先:{source}が存在しません")

            # 各プロパティに対するマッピング処理
            self._new_schema = {}
            for schema_property, components in self._mapping_definition.items():
                link_list = {}
                source = components.get("source")
                storage_path = components.get("value")
                definition = {schema_property: definition}
                # 対応するデータがGRDMに存在しない場合
                if storage_path is None:
                    results = []
                    self._new_schema = self._create_schema(definition, results, link_list)
                    continue

                try:
                    if source in source_data:
                        self._filter_metadata(
                            source_data[source], definition, link_list)

                    else:
                        raise MappingDefinitionError(
                            f"メタデータ取得先:{source}が存在しません"({schema_property}))
                # GRDMに指定したデータが存在しない場合は次のプロパティへ
                except NotFoundKeyError as e:
                    results = []
                    self._new_schema = self._create_schema(definition, results, link_list)
                    logger.error(e)
                    continue

        except MetadataTypeError as e:
            logger.error(e)
            raise MetadataTypeError("データの変換に失敗しました。") from e

        except MappingDefinitionError as e:
            logger.error(e)
            raise MappingDefinitionError("マッピング定義に誤りがあります。") from e

        except NotFoundSourceError as e:
            logger.error(e)
            raise NotFoundSourceError("メタデータ取得先の特定に失敗しました。") from e

        return self._new_schema

    def _find_metadata_sources(self) -> list:
        """メタデータの取得先を特定するメソッドです。

        Returns:
            list: メタデータの取得先の一覧

        """
        metadata_sources = set()

        for components in self._mapping_definition.values():
            source = components.get("source")
            if source is not None:
                metadata_sources.add(components[source])

        return list(metadata_sources)

    def _filter_metadata(self, source: dict, definition: dict, link_list: dict, key_path: str = None):
        """必要なメタデータのみを取得するメソッドです。

        Args:
            source (dict): ストレージから取得した全データ
            definition (dict): スキーマのプロパティ一つ当たりの定義
            link_list (dict): 対応するリストの情報
            key_path (str, optional): 取得するデータを示す文字列。デフォルトはNone

        Raises:
            NotFoundKeyError:　データの構造を示すキーが存在しない
            MappingDefinitionError:　マッピング定義に誤りがある

        """
        schema_property, components = definition.items()
        is_list = components.get("list")
        storage_path = key_path or components.get("value")
        keys = storage_path.split(".")

        # キーを一つずつ取り出して処理を行う。
        for index, key in enumerate(keys[:-1]):
            if key not in source:
                raise NotFoundKeyError(
                    f"一致するキー名：{key}が見つかりません({schema_property})")

            # 値がリスト構造の場合
            if isinstance(source[key], list):
                is_link = is_list.get(key)
                if is_link is None:
                    raise MappingDefinitionError(
                        f"リスト：{key}が定義されていません({schema_property})")

                # 対応するリストが存在する場合
                if not is_link.isdigit():
                    for i, item in enumerate(source[key]):
                        link_list[is_link] = i + 1  # 対応するリストの項目数を示す
                        try:
                            self._filter_metadata(
                                item, definition, link_list, '.'.join(keys[index+1:]))
                        except NotFoundKeyError as e:
                            results = []
                            self._new_schema = self._create_schema(definition, results, link_list)
                            logger.error(e)
                            continue
                # 対応するリストが存在しない場合
                else:
                    if 0 <= is_link < len(source[key]): # マッピング定義で指定したインデックス
                        source = source[key][index]
                    else:
                        raise MappingDefinitionError(
                            f"指定されたインデックス:{is_link}が存在しません({schema_property})")

            # 値がdict構造の場合
            elif isinstance(source[key], dict):
                if key not in is_list:
                    source = source[key]
                else:
                    raise MappingDefinitionError(
                        f"オブジェクト：{key}がリストとして定義されています。({schema_property})")

            else:
                raise MappingDefinitionError(
                    f"データ構造が定義と異なっています({schema_property})")

        # 最終キーに対する処理
        final_key = keys[-1]
        if final_key not in source:
            raise NotFoundKeyError(
                f"メタデータに一致するキー名{final_key}が見つかりません({schema_property})")

        results = []
        # 値がリスト構造の場合
        if isinstance(source[final_key], list):
            is_link = is_list.get(final_key)
            if is_link:
                # 対応するリストが存在する場合
                if not is_link.isdigit():
                    for i, item in enumerate(source[final_key]):
                        link_list[is_link] = i + 1
                        results = []
                        results.extend(item)
                    self._new_schema = self._create_schema(definition, results, link_list)
                # 対応するリストが存在しない場合
                else:
                    if len(source[final_key]) > 0 and 0 <= is_link < len(source[final_key]):
                        results.extend(source[final_key][is_link])
                    else:
                        raise MappingDefinitionError(
                            f"指定されたインデックスが存在しません({schema_property})")

                    self._new_schema = self._create_schema(definition, results, link_list)

            # 通常のリストの処理
            else:
                results.extend(source.get(final_key, []))
                self._new_schema = self._create_schema(definition, results, link_list)

        # キーの数が不足している場合
        elif isinstance(source[final_key], dict):
            raise MappingDefinitionError(
                f"データ構造が定義と異なっています({schema_property})")

        # 値がリストではない場合
        else:
            value = source.get(final_key)
            if value is not None:
                results.append(value)
            self._new_schema = self._create_schema(definition, results, link_list)

    def _create_schema(self, definition: dict, results: list, link_list: dict) -> dict:
        """スキーマを作成し、データを挿入するメソッドです。

        Args:
            definition (dict): スキーマのプロパティ一つ当たりの定義
            results (list): ストレージから取得したデータ
            link_list (dict): 対応するリストの情報

        return:
            dict: データを挿入したスキーマ

        Raises:
            MappingDefinitionError: マッピング定義に誤りがある
            MetadataTypeError: データの型が変換できない

        """
        schema_path, components = definition.items()
        keys = schema_path.split('.')
        current_level = self._new_schema

        for key in keys[:-1]:
            # リストの場合
            if "[]" in key:
                base_key = key.replace("[]", "")
                # キーが存在しない場合、新しく作成する。
                if base_key not in current_level:
                    current_level[base_key] = [{}]
                    current_level = current_level[base_key]
                    continue
                # リスト構造以外が存在する場合
                elif not isinstance(current_level[base_key], list):
                    raise MappingDefinitionError(
                        f"マッピング定義に誤りがあります({schema_path})")

                index = link_list.get(base_key)
                # リストが対応している場合
                if index is not None:
                    while index > len(current_level[base_key]):
                        current_level[base_key].append({})
                    current_level = current_level[base_key][index-1]
                # リストが対応していない場合
                else:
                    if len(current_level[base_key]) <= 1:
                        current_level = current_level[base_key]
                    else:
                        raise MappingDefinitionError(
                            f"マッピング定義に誤りがあります({schema_path})")
            # dictの場合
            else:
                if key not in current_level:
                    current_level[key] = {}
                elif not isinstance(current_level[key], dict):
                    raise MappingDefinitionError(
                        f"マッピング定義に誤りがあります({schema_path})")
                current_level = current_level[key]

        # 最終キーの処理
        final_key = keys[-1]
        type = components.get("type")
        converted_results = []
        # データが存在する場合、型チェックを行う
        if results:
            try:
                converted_results = self._convert_data_type(results, type)

            except MappingDefinitionError as e:
                raise MappingDefinitionError(
                    f"type:{type}は有効な型ではありません({schema_path})") from e

            except Exception as e:
                raise MetadataTypeError(
                    f"型変換エラー：{results}を{type}に変換できません({schema_path}):{e}") from e

        # スキーマの定義がリストの場合
        if "[]" in final_key:
            base_key = final_key.replace("[]", "")
            current_level.setdefault(base_key, [])
            if converted_results:
                current_level[base_key].extend(converted_results)
        # スキーマの定義がリストではない場合
        else:
            current_level[final_key] = converted_results[0] if converted_results else None

        return current_level

    def _convert_data_type(self, results: list, type: Optional[str]) -> list:
        """ストレージから取得したデータをスキーマ定義の要求する型に変換するメソッドです。

        Args:
            results (list): ストレージから取得したデータ
            type (Optional[str]): マッピング定義に記載されたスキーマ定義の要求する型

        Returns:
            list: スキーマの要求する型に変換したデータ

        Raises:
            MetadataTypeError: データの型が変換できない
            MappingDefinitionError: マッピング定義に誤りがある

        """
        converted_results = []
        for result in results:

            if type == "string":
                converted_results.append(str(result))

            elif type == "boolean":
                if isinstance(result, bool):
                    converted_results.append(result)
                elif isinstance(result, str):
                    if result.lower() == "true":
                        converted_results.append(True)
                    elif result.lower() == "false":
                        result = False
                        converted_results.append(False)
                    else:
                        raise MetadataTypeError()
                else:
                    raise MetadataTypeError()

            elif type == "number":
                converted_results.append(
                    float(result) if '.' in str(result) else int(result))

            else:
                raise MappingDefinitionError()

        return converted_results

class GrdmAccess():

    """GRDMへのアクセスを行うメソッドをまとめたクラスです。

    Attributes:
        class:
            _DOMAIN(str):GRDMのドメイン
        instance:
            _token(str):アクセストークン
            _project_id(str):プロジェクトid
            _is_authenticated(bool):認証結果

    """

    def check_authentication(self, token: str, project_id: str) -> bool:
        """アクセス権の認証を行うメソッド"""

    def _check_token_valid(self) -> bool:
        """トークンの存在とアクセス権の有無を確認するメソッドです。"""

    def _check_project_metadata(self) -> bool:
        """プロジェクトメタデータへのアクセスが可能か調べるメソッドです。"""

    def _check_file_metadata(self) -> bool:
        """ファイルメタデータへのアクセスが可能か調べるメソッドです。"""

    def _check_project_info(self) -> bool:
        """プロジェクト情報へのアクセスが可能か調べるメソッドです。"""

    def _check_member_info(self) -> bool:
        """メンバー情報へのアクセスが可能か調べるメソッドです。"""

    def get_project_metadata(self) -> dict:
        """プロジェクトメタデータを取得するメソッドです。"""

    def get_file_metadata(self) -> dict:
        """ファイルメタデータを取得するメソッドです。"""

    def get_project_info(self) -> dict:
        """プロジェクト情報を取得するメソッドです。"""

    def get_member_info(self) -> dict:
        """メンバー情報を取得するメソッドです。"""
