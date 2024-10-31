"""GRDMストレージに関するモジュールです。"""

from typing import Optional, Any
from logging import getLogger
import requests

from dg_mm.models.mapping_definition import DefinitionManager
from dg_mm.errors import (
    UnauthorizedError,
    AccessDeniedError,
    APIError,
    InvalidTokenError,
    InvalidIdError,
    DataFormatError,
    MappingDefinitionError,
    MetadataTypeError,
    NotFoundKeyError,
    MetadataNotFoundError
)
from dg_mm.util import PackageFileReader

logger = getLogger(__name__)


class GrdmMapping():
    """GRDMとのマッピングを行うクラスです。

    Attributes:
        instance:
            _mapping_definition(dict): マッピング定義
            _new_schema(dict): 作成するスキーマ

    """

    def mapping_metadata(self, schema: str, token: str, project_id: str, filter_properties: list = None, project_metadata_id: str = None) -> dict:
        """スキーマの定義に従いマッピングを行うメソッドです。

        Args:
            schema (str): スキーマを一意に定める文字列
            token (str): GRDMの認証に用いるトークン
            project_id (str): GRDMのプロジェクトを一意に定めるID
            filter_properties (list): スキーマの絞り込みに用いるプロパティの一覧。デフォルトはNone
            project_metadata_id (str): プロジェクトメタデータを一意に定めるID。デフォルトはNone.

        Returns:
            dict: スキーマにデータを挿入したもの

        Raises:
            MappingDefinitionError: マッピング定義の内容に誤りがある
            NotFoundKeyError: 一致するキーが見つからない
            MetadataTypeError: 型の変換ができない
            DataFormatError: データの形式に誤りがある

        """
        # GRDMの認証
        grdm_access = GrdmAccess()
        grdm_access.check_authentication(token, project_id)

        # マッピング定義の取得
        storage = "GRDM"
        self._mapping_definition = DefinitionManager.get_and_filter_mapping_definition(schema, storage, filter_properties)

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
                error_sources = []
                for source in metadata_sources:
                    if source in source_mapping:
                        source_data[source] = source_mapping[source](project_metadata_id=project_metadata_id)
                    else:
                        error_sources.append(source)
                if error_sources:
                    raise MappingDefinitionError(
                        f"メタデータ取得先:{error_sources}が存在しません")

            # 各プロパティに対するマッピング処理
            new_schema = {}
            error_keys = []
            error_types = []
            for schema_property, components in self._mapping_definition.items():
                schema_link_list = {}
                source = components.get("source")
                storage_path = components.get("value")
                # 対応するデータがGRDMに存在しない場合
                if storage_path is None:
                    type = components.get("type")
                    storage_data = []
                    new_schema = self._add_property(
                        new_schema, schema_property, type, storage_data, schema_link_list)
                    continue

                storage_keys = storage_path.split(".")
                try:
                    new_schema = self._extract_and_insert_metadata(
                        new_schema, source_data[source], schema_property, components, schema_link_list, storage_keys)

                except NotFoundKeyError as e:
                    if isinstance(e.args[0], list):
                        error_keys.extend(e.args[0])
                    else:
                        error_keys.append(str(e))
                    continue

                except MetadataTypeError as e:
                    error_types.append(str(e))

            if error_keys and error_types:
                raise DataFormatError(
                    f"キーの不一致が確認されました。:{error_keys}, データの変換に失敗しました。：{error_types}")
            elif error_keys:
                raise NotFoundKeyError(f"キーの不一致が確認されました。:{error_keys}")
            elif error_types:
                raise MetadataTypeError(f"データの変換に失敗しました。：{error_types}")

        except (MetadataTypeError, MappingDefinitionError,
                NotFoundKeyError, DataFormatError) as e:
            logger.error(e)
            raise

        return new_schema

    def _find_metadata_sources(self) -> list:
        """メタデータの取得先を特定するメソッドです。

        Returns:
            list: メタデータの取得先の一覧

        """
        metadata_sources = set()

        for components in self._mapping_definition.values():
            source = components.get("source")
            if source is not None:
                metadata_sources.add(source)

        return list(metadata_sources)

    def _extract_and_insert_metadata(
            self, new_schema: dict, source: dict, schema_property: str,
            components: dict, schema_link_list: dict, storage_keys: list) -> dict:
        """メタデータの取り出しとスキーマへの挿入を行うメソッドです。

        マッピング定義で指定されたデータをストレージのデータから取り出し、スキーマへと挿入したものを返します。

        Args:
            new_schema (dict): 取得したデータを挿入するスキーマ
            source (dict): マッピング定義に記載された取得先から得たストレージのデータ
            schema_property (str): スキーマのプロパティまでのキーをつなげた文字列
            components (dict): マッピング定義情報。取得するデータの場所や構造、スキーマの求めるデータ型の情報が記載されています。
            schema_link_list (dict): ストレージのリストと対応したスキーマのリストの情報。リストの項目数を保持しています。
            storage_keys (list): ストレージから取得するデータまでのキーのリスト

        Returns:
            dict: 取得したデータを挿入したスキーマ

        """
        # キーを一つずつ取り出して処理を行う
        for index, key in enumerate(storage_keys[:-1]):
            source = self._check_and_handle_key_structure(
                new_schema, source, schema_property, components, schema_link_list, storage_keys, index, key)

            # ストレージのデータにあるリストと対応するリストがスキーマに存在する場合、このメソッドを再帰的に呼び出してデータの取り出しと挿入を行った後、Noneを返します。
            # そのため、sourceがNoneの場合は以降のデータ取り出し、挿入処理をスキップします。
            if source is None:
                return new_schema

        # 最終キーに対する処理。キーの値を取り出し、スキーマに挿入したものを返します。
        final_key = storage_keys[-1]
        new_schema = self._get_and_insert_final_key_value(
            new_schema, source, schema_property, components, final_key, schema_link_list)

        return new_schema

    def _check_and_handle_key_structure(
            self, new_schema: dict, source: dict, schema_property: str, components: dict,
            schema_link_list: dict, storage_keys: list, index: int, key: str) -> Optional[dict]:
        """キーの値がlistかdictかを判定し、対応した処理を実行するメソッドです。

        listだった場合は_handle_listを呼び出しリストの定義に応じた処理を実行し、dictだった場合はsourceをそのキーの値に更新します。

        Args:
            new_schema (dict): 取得したデータを挿入するスキーマ
            source (dict): マッピング定義に記載された取得先から得たストレージのデータ
            schema_property (str): スキーマのプロパティまでのキーをつなげた文字列
            components (dict): マッピング定義情報。取得するデータの場所や構造、スキーマの求めるデータ型の情報が記載されています。
            schema_link_list (dict): ストレージのリストと対応したスキーマのリストの情報。リストの項目数を保持しています。
            storage_keys (list): ストレージから取得するデータまでのキーのリスト
            index (int): 処理中のキーのインデックス
            key (str): 処理中のキー

        Returns:
            Optional[dict]: ストレージのデータから処理中のキーで検索した値のデータ。
                _handle_list内で再帰的な処理が実行された場合はNoneが返ってくるので、このメソッドの戻り値もNoneとなります。

        Raises:
            NotFoundKeyError: データの構造を示すキーが存在しない
            MappingDefinitionError: マッピング定義に誤りがある

        """
        if key not in source:
            raise NotFoundKeyError(
                f"{key}と一致するストレージのキーが見つかりませんでした。({schema_property})")
        # 値がリスト構造の場合
        if isinstance(source[key], list):
            source = self._handle_list(
                new_schema, source, schema_property, components, schema_link_list, storage_keys, index, key)

        # 値がdict構造の場合
        elif isinstance(source[key], dict):
            link_list_info = components.get("list")
            complete_storage_keys = components.get("value").split(".")
            current_key_index = index + len(complete_storage_keys) - len(storage_keys)
            link_list_info = link_list_info.get(".".join(complete_storage_keys[:current_key_index + 1])) if link_list_info else None
            if link_list_info:
                raise MappingDefinitionError(
                    f"オブジェクト：{'.'.join(complete_storage_keys[:current_key_index + 1])}がリストとして定義されています。({schema_property})")
            else:
                source = source[key]

        else:
            raise MappingDefinitionError(
                f"データ構造が定義と異なっています。({schema_property})")

        return source

    def _handle_list(
            self, new_schema: dict, source: dict, schema_property: str, components: dict,
            schema_link_list: dict, storage_keys: list, index: int, key: str) -> Optional[dict]:
        """リスト構造だった場合の処理を実行するメソッドです。

        スキーマに対応するリストが存在する場合は_extract_and_insert_metadataを再帰的に呼び出し、データの取り出しとスキーマへの挿入を行います。
        存在しない場合は、マッピング定義で指定されたインデックスのデータを返します。

        Args:
            new_schema (dict): 取得したデータを挿入するスキーマ
            source (dict): マッピング定義に記載された取得先から得たストレージのデータ
            schema_property (str): スキーマのプロパティまでのキーをつなげた文字列
            components (dict): マッピング定義情報。取得するデータの場所や構造、スキーマの求めるデータ型の情報が記載されています。
            schema_link_list (dict): ストレージのリストと対応したスキーマのリストの情報。リストの項目数を保持しています。
            storage_keys (list): ストレージから取得するデータまでのキーのリスト
            index (int): 処理中のキーのインデックス
            key (str): 処理中のキー

        Returns:
            Optional[dict]: ストレージデータから処理中のキーで検索して得られたリストの指定されたインデックスのデータ。再帰的な呼びだしを行った場合はNoneを返します。

        Raises:
            MappingDefinitionError: マッピング定義に誤りがある
            NotFoundKeyError: データの構造を示すキーが存在しない

        """
        link_list_info = components.get("list")
        complete_storage_keys = components.get("value").split(".")
        current_key_index = index + len(complete_storage_keys) - len(storage_keys)
        link_list_info = link_list_info.get(".".join(complete_storage_keys[:current_key_index + 1])) if link_list_info else None

        if link_list_info is None:
            raise MappingDefinitionError(f"リスト：{key}の定義が不足しています。({schema_property})")

        # 対応するリストが存在する場合
        if isinstance(link_list_info, str):
            error_keys = []
            storage_keys = storage_keys[index+1:]
            for i, item in enumerate(source[key]):
                schema_link_list[link_list_info] = i + 1

                try:
                    new_schema = self._extract_and_insert_metadata(
                        new_schema, item, schema_property, components, schema_link_list, storage_keys)

                except NotFoundKeyError as e:
                    error_keys.append(str(e))
                    continue
            if error_keys:
                raise NotFoundKeyError(error_keys)

            return

        # 対応するリストが存在しない場合
        else:
            if 0 <= link_list_info < len(source[key]):
                source = source[key][link_list_info]
                return source
            else:
                raise MappingDefinitionError(
                    f"指定されたインデックス:{link_list_info}が存在しません({schema_property})")

    def _get_and_insert_final_key_value(
            self, new_schema: dict, source: dict, schema_property: str,
            components: dict, final_key: str, schema_link_list: dict) -> dict:
        """ストレージの最終キーの値を取得し、スキーマに挿入するメソッドです。

        Args:
            new_schema (dict): 取得したデータを挿入するスキーマ
            source (dict): マッピング定義に記載された取得先から得たストレージのデータ
            schema_property (str): スキーマのプロパティまでのキーをつなげた文字列
            components (dict): マッピング定義情報。取得するデータの場所や構造、スキーマの求めるデータ型の情報が記載されています。
            final_key (str): 取得するデータのキー
            schema_link_list (dict): ストレージのリストと対応したスキーマのリストの情報。リストの項目数を保持しています。

        Returns:
            dict: データを挿入したスキーマ

        Raises:
            MappingDefinitionError: マッピング定義に誤りがある

        """
        storage_data = []
        type = components.get("type")

        if final_key not in source:
            new_schema = self._add_property(
                new_schema, schema_property, type, storage_data, schema_link_list)
            return new_schema

        # 値がリスト構造の場合
        if isinstance(source[final_key], list):
            link_list_info = components.get("list")
            complete_storage_keys = components.get("value").split(".")
            link_list_info = link_list_info.get(".".join(complete_storage_keys)) if link_list_info else None
            if link_list_info:
                # 対応するリストが存在する場合
                if isinstance(link_list_info, str):
                    for i, item in enumerate(source[final_key]):
                        schema_link_list[link_list_info] = i + 1
                        storage_data = []
                        storage_data.append(item)
                        new_schema = self._add_property(
                            new_schema, schema_property, type, storage_data, schema_link_list)
                    return new_schema
                # 対応するリストが存在しない場合
                else:
                    if len(source[final_key]) > 0 and 0 <= link_list_info < len(source[final_key]):
                        storage_data.append(source[final_key][link_list_info])
                        new_schema = self._add_property(
                            new_schema, schema_property, type, storage_data, schema_link_list)
                    else:
                        raise MappingDefinitionError(
                            f"指定されたインデックスが存在しません({schema_property})")

                    return new_schema

            # 通常のリストの処理
            else:
                storage_data.extend(source.get(final_key, []))
                new_schema = self._add_property(
                    new_schema, schema_property, type, storage_data, schema_link_list)
                return new_schema

        # キーの数が不足している場合
        elif isinstance(source[final_key], dict):
            raise MappingDefinitionError(
                f"データ構造が定義と異なっています({schema_property})")

        # 値がリストではない場合
        else:
            value = source.get(final_key)
            if value is not None:
                storage_data.append(value)
            new_schema = self._add_property(
                new_schema, schema_property, type, storage_data, schema_link_list)
            return new_schema

    def _add_property(
            self, new_schema: dict, schema_property: str,
            type: Optional[str], storage_data: list, schema_link_list: dict) -> dict:
        """取得したデータと対応したプロパティをスキーマに追加するメソッドです。

        スキーマに引数で指定したプロパティを追加し、そこに取得したデータを挿入します。

        Args:
            new_schema(dict): プロパティを追加するスキーマ
            schema_property(str): 追加するスキーマのプロパティまでのキーをつなげた固有の文字列
            type(Optional[str]): スキーマの要求するデータの型
            storage_data (list): ストレージから取得したデータ
            schema_link_list (dict): ストレージのリストと対応したスキーマのリストの情報。リストの項目数を保持している。

        return:
            dict: データを挿入したスキーマ

        Raises:
            MappingDefinitionError: マッピング定義に誤りがある
            MetadataTypeError: データの型が変換できない

        """
        keys = schema_property.split('.')
        current_schema = new_schema

        for index, key in enumerate(keys[:-1]):
            # リストの場合
            if "[]" in key:
                base_key = key.replace("[]", "")
                # キーが存在しない場合、新しく作成する。
                if base_key not in current_schema:
                    current_schema[base_key] = [{}]
                    current_schema = current_schema[base_key][0]
                    continue
                # リスト構造以外が存在する場合
                elif not isinstance(current_schema[base_key], list):
                    raise MappingDefinitionError(
                        f"マッピング定義に誤りがあります({schema_property})")

                base_keys = [key.replace("[]", "") for key in keys[:index + 1]]
                link_list_info = schema_link_list.get(".".join(base_keys))

                # リストが対応している場合
                if link_list_info is not None:
                    counts = link_list_info - len(current_schema[base_key])
                    if counts > 0:
                        for _ in range(counts):
                            current_schema[base_key].append({})
                    current_schema = current_schema[base_key][link_list_info - 1]
                # リストが対応していない場合
                else:
                    if len(current_schema[base_key]) <= 1:
                        current_schema = current_schema[base_key][0]
                    else:
                        raise MappingDefinitionError(
                            f"マッピング定義に誤りがあります({schema_property})")
            # dictの場合
            else:
                if key not in current_schema:
                    current_schema[key] = {}
                elif not isinstance(current_schema[key], dict):
                    raise MappingDefinitionError(
                        f"マッピング定義に誤りがあります({schema_property})")
                current_schema = current_schema[key]

        # 最終キーの処理
        final_key = keys[-1]
        converted_storage_data = []
        # データが存在する場合、型チェックを行う
        if storage_data:
            try:
                converted_storage_data = self._convert_data_type(
                    storage_data, type)

            except MappingDefinitionError as e:
                raise MappingDefinitionError(
                    f"type:{type}は有効な型ではありません({schema_property})") from e

            except Exception as e:
                raise MetadataTypeError(
                    f"型変換エラー：{storage_data}を{type}に変換できません({schema_property})") from e

        # スキーマの定義がリストの場合
        if "[]" in final_key:
            base_key = final_key.replace("[]", "")
            current_schema.setdefault(base_key, [])
            if converted_storage_data:
                current_schema[base_key].extend(converted_storage_data)
        # スキーマの定義がリストではない場合
        else:
            current_schema[final_key] = converted_storage_data[0] if converted_storage_data else None

        return new_schema

    def _convert_data_type(self, data: list, type: Optional[str]) -> list:
        """データの型を要求された型へと変換するメソッドです。

        Args:
            data (list): 型の変換を行うデータ
            type (Optional[str]): 変換する型の情報

        Returns:
            list: 型を変換したデータ

        Raises:
            MetadataTypeError: データの型が変換できない
            MappingDefinitionError: マッピング定義に誤りがある

        """
        converted_data = []
        for value in data:

            if type == "string":
                converted_data.append(str(value))

            elif type == "boolean":
                if isinstance(value, bool):
                    converted_data.append(value)
                elif isinstance(value, str):
                    if value.lower() == "true":
                        converted_data.append(True)
                    elif value.lower() == "false":
                        value = False
                        converted_data.append(False)
                    else:
                        raise MetadataTypeError()
                else:
                    raise MetadataTypeError()

            elif type == "number":
                converted_data.append(
                    float(value) if '.' in str(value) else int(value))

            else:
                raise MappingDefinitionError()

        return converted_data


class GrdmAccess():

    """GRDMへのアクセスを行うメソッドをまとめたクラスです。

    Attributes:
        class:
            _CONFIG_PATH(str):GRDMの設定ファイルのパス
            _ALLOWED_SCOPES(list):スコープの権限
        instance:
            _token(str):アクセストークン
            _project_id(str):プロジェクトid
            _config_file(ConfigParser):GRDMの設定ファイルのインスタンス
            _domain(str):GRDMのドメイン
            _timeout(float):リクエストのタイムアウトする時間(秒)
            _max_requests(int):リクエスト回数の上限
    """
    _CONFIG_PATH = "data/storage/grdm.ini"
    _ALLOWED_SCOPES = ["osf.full_write", "osf.full_read"]

    def __init__(self):
        """インスタンスの初期化メソッド"""
        self._config_file = PackageFileReader.read_ini(GrdmAccess._CONFIG_PATH)
        self._domain = self._config_file["settings"]["domain"]
        self._timeout = self._config_file["settings"].getfloat("timeout")
        self._max_requests = self._config_file["settings"].getint("max_requests")
        self._is_authenticated = None

    def check_authentication(self, token: str, project_id: str) -> bool:
        """アクセス権の認証を行うメソッドです。

        Args:
            token (str):パーソナルアクセストークン
            project_id (str):プロジェクトID

        Returns:
            bool:認証結果を返す
        """
        self._token = token
        self._project_id = project_id
        self._is_authenticated = all((self._check_token_valid(), self._check_project_id_valid()))
        return self._is_authenticated

    def _check_token_valid(self) -> bool:
        """トークンの存在とアクセス権の有無を確認するメソッドです。

        Returns:
            bool:認証結果を返す

        Raises:
            InvalidTokenError:トークン不正のエラー
            AccessDeniedError:アクセス権不正のエラー
            APIError:APIのサーバーエラー、タイムアウト
        """
        base_url = self._config_file["url"]["token"]
        url = base_url.format(domain=self._domain)
        headers = {'Authorization': f'Bearer {self._token}'}
        try:
            response = requests.get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error(f"InvalidTokenError: {e}")
                raise InvalidTokenError("認証に失敗しました")
            elif response.status_code >= 500:
                logger.error(f"API server error: {e}")
                raise APIError("APIサーバーでエラーが発生しました")
            else:
                logger.error(f"Unexpected HTTP error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            raise APIError("APIリクエストがタイムアウトしました")
        else:
            scope = data["scope"]
            if any(element in scope for element in GrdmAccess._ALLOWED_SCOPES):
                return True
            else:
                logger.error(f"token permisson error: {scope}")
                raise AccessDeniedError("トークンのアクセス権が不足しています")

    def _check_project_id_valid(self) -> bool:
        """プロジェクトIDの存在とアクセス権の有無を確認するメソッドです。

        Returns:
            bool: 結果を返す

        Raises:
            AccessDeniedError:アクセス権不正
            InvalidIdError:プロジェクト不正
            APIError:APIのサーバーエラー、タイムアウト
        """
        base_url = self._config_file["url"]["project_info"]
        url = base_url.format(domain=self._domain, project_id=self._project_id)
        headers = {'Authorization': f'Bearer {self._token}'}
        try:
            response = requests.get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                logger.error(f"Project permisson error: {e}")
                raise AccessDeniedError("プロジェクトへのアクセス権がありません")
            elif response.status_code == 404:
                logger.error(f"Project not found: {e}")
                raise InvalidIdError("プロジェクトが存在しません")
            elif response.status_code == 410:
                logger.error(f"Project deleted: {e}")
                raise InvalidIdError("プロジェクトが削除されています")
            elif response.status_code >= 500:
                logger.error(f"API server error: {e}")
                raise APIError("APIサーバーでエラーが発生しました")
            else:
                logger.error(f"Unexpected HTTP error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            raise APIError("APIリクエストがタイムアウトしました")
        return bool(result)

    def get_project_metadata(self, project_metadata_id: str = None, **kwargs: Any) -> dict:
        """プロジェクトメタデータを取得するメソッドです。

        Args:
            project_metadata_id(str): プロジェクトメタデータのID
            **kwargs(Any): 使用しない引数の受け皿

        Returns:
            dict: APIから取得したプロジェクトメタデータを返す。
                プロジェクトメタデータのIDが指定されている場合は、idが一致するデータのみが含まれるレスポンスを返す。
                プロジェクトメタデータのIDが指定されていない場合は、作成日が最も新しいデータ1件のみが含まれるレスポンスを返す。

        Raises:
            UnauthorizedError:認証処理を実行せずに実行した場合のエラー
            MetadataNotFoundError: 存在しないプロジェクトメタデータIDを指定した場合のエラー
            APIError:APIのサーバーエラー、タイムアウト
        """
        if not self._is_authenticated:
            logger.error(f"Executed without authentication process")
            raise UnauthorizedError("認証されていません")
        if project_metadata_id is None:
            base_url = self._config_file["url"]["project_metadata"]
            url = base_url.format(domain=self._domain, project_id=self._project_id)
            params = {"sort": "-date_created"}
        else:
            base_url = self._config_file["url"]["project_metadata_by_id"]
            url = base_url.format(domain=self._domain)
            params = {"filter[id]": f"{project_metadata_id}"}

        headers = {'Authorization': f'Bearer {self._token}'}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()

            # IDを指定しない場合は作成日が最新のデータ
            if project_metadata_id is None:
                # 先頭のデータが最新
                if len(data["data"]) > 0:
                    target = data["data"][0]
                    data["data"].clear()
                    data["data"].append(target)
                # 登録件数が0件の場合はそのまま
                return data
            # IDを指定する場合はIDが一致するデータ
            else:
                if len(data["data"]) > 0:
                    # 他のプロジェクトのプロジェクトメタデータでないことの確認
                    if data["data"][0]["relationships"]["registered_from"]["data"]["id"] == self._project_id:
                        return data
                    else:
                        raise MetadataNotFoundError("指定したIDのプロジェクトメタデータが存在しません")
                else:
                    raise MetadataNotFoundError("指定したIDのプロジェクトメタデータが存在しません")

        except requests.exceptions.HTTPError as e:
            if response.status_code >= 500:
                logger.error(f"API server error: {e}")
                raise APIError("APIサーバーでエラーが発生しました")
            else:
                logger.error(f"Unexpected HTTP error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            raise APIError("APIリクエストがタイムアウトしました")

    def get_file_metadata(self, **kwargs: Any) -> dict:
        """ファイルメタデータを取得するメソッドです。

        Args:
            **kwargs(Any): 使用しない引数の受け皿

        Returns:
            dict: APIから取得したファイルメタデータを返す

        Raises:
            UnauthorizedError: 認証処理を実行せずに実行した場合のエラー
            APIError:APIのサーバーエラー、タイムアウト
        """
        if not self._is_authenticated:
            logger.error(f"Executed without authentication process")
            raise UnauthorizedError("認証されていません")
        base_url = self._config_file["url"]["file_metadata"]
        url = base_url.format(domain=self._domain, project_id=self._project_id)
        headers = {'Authorization': f'Bearer {self._token}'}
        try:
            response = requests.get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                # アドオンが無効の場合もエラーにしない
                result = {}
            elif response.status_code >= 500:
                logger.error(f"API server error: {e}")
                raise APIError("APIサーバーでエラーが発生しました")
            else:
                logger.error(f"Unexpected HTTP error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            raise APIError("APIリクエストがタイムアウトしました")
        return result

    def get_project_info(self, **kwargs: Any) -> dict:
        """プロジェクト情報を取得するメソッドです。

        Args:
            **kwargs(Any): 使用しない引数の受け皿

        Returns:
            dict: APIから取得したプロジェクト情報を返す

        Raises:
            UnauthorizedError: 認証処理を実行せずに実行した場合のエラー
            APIError:APIのサーバーエラー、タイムアウト
        """
        if not self._is_authenticated:
            logger.error(f"Executed without authentication process")
            raise UnauthorizedError("認証されていません")
        base_url = self._config_file["url"]["project_info"]
        url = base_url.format(domain=self._domain, project_id=self._project_id)
        headers = {'Authorization': f'Bearer {self._token}'}
        try:
            response = requests.get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code >= 500:
                logger.error(f"API server error: {e}")
                raise APIError("APIサーバーでエラーが発生しました")
            else:
                logger.error(f"Unexpected HTTP error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            raise APIError("APIリクエストがタイムアウトしました")
        return result

    def get_member_info(self, **kwargs: Any) -> dict:
        """メンバー情報を取得するメソッドです。

        メンバーが11人以上の場合は1回目のレスポンスの"data"に2回目以降のレスポンスの"data"を末尾に追加する。

        Args:
            **kwargs(Any): 使用しない引数の受け皿

        Returns:
            dict: APIから取得したメンバー情報を返す。11件以上の場合は以下の形式になる。
                - "data": 登録されているすべてのメンバー情報が含まれる。
                - "links": 1ページ目の情報が入っている。
                - "meta": 1ページ目の情報が入っている。

        Raises:
            UnauthorizedError: 認証処理を実行せずに実行した場合のエラー
            APIError:APIのサーバーエラー、タイムアウト、リクエスト回数の上限
        """
        if not self._is_authenticated:
            logger.error(f"Executed without authentication process")
            raise UnauthorizedError("認証されていません")
        base_url = self._config_file["url"]["member_info"]
        url = base_url.format(domain=self._domain, project_id=self._project_id)
        headers = {'Authorization': f'Bearer {self._token}'}
        request_count = 0
        result = None
        try:
            while url:
                response = requests.get(url, headers=headers, timeout=self._timeout)
                response.raise_for_status()
                data = response.json()
                if result is None:
                    result = data
                else:
                    result["data"].extend(data["data"])
                url = data["links"].get("next")
                request_count += 1
                if request_count >= self._max_requests:
                    raise APIError("リクエスト回数が上限を超えました")
        except requests.exceptions.HTTPError as e:
            if response.status_code >= 500:
                logger.error(f"API server error: {e}")
                raise APIError("APIサーバーでエラーが発生しました")
            else:
                logger.error(f"Unexpected HTTP error: {e}")
                raise
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            raise APIError("APIリクエストがタイムアウトしました")
        return result
