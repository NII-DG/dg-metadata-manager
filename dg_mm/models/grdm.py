"""GRDMストレージに関するモジュールです。"""

import configparser
from logging import getLogger

import requests

from dg_mm.exceptions import (
    UnauthorizedError,
    AccessDeniedError,
    APIError,
    InvalidTokenError,
    InvalidProjectError
)

logger = getLogger(__name__)

class GrdmMapping():
    """GRDMストレージのマッピングクラスです。

    Attributes:
        instance:
            _mapping_definition(dict):絞り込まれたマッピング定義

    """

    def mappping_metadata(self, Schema: str, token: str, project_id: str, option: list = None) -> dict:
        """スキーマの定義に従いマッピングを行うメソッドです。"""

    def _find_metadata_sources(self) -> list:
        """メタデータの取得先を特定するメソッドです。"""

    def _filter_metadata(self, option: list = None) -> dict:
        """メタデータの絞り込みを行うメソッドです。"""

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
    _CONFIG_PATH = "dg_mm/data/storage/grdm.ini"
    _ALLOWED_SCOPES = ["osf.full_write", "osf.full_read"]

    def __init__(self):
        """インスタンスの初期化メソッド"""
        self._config_file = configparser.ConfigParser()
        self._config_file.read(GrdmAccess._CONFIG_PATH)
        self._domain = self._config_file["settings"]["domain"]
        self._timeout = self._config_file["settings"].getfloat("timeout")
        self._max_requests = self._config_file["settings"].getint("max_requests")

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
            InvalidProjectError:プロジェクト不正
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
                raise InvalidProjectError("プロジェクトが存在しません")
            elif response.status_code == 410:
                logger.error(f"Project deleted: {e}")
                raise InvalidProjectError("プロジェクトが削除されています")
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

    def get_project_metadata(self) -> dict:
        """プロジェクトメタデータを取得するメソッドです。

        登録されているプロジェクトメタデータの数が11個件以上の場合は1回目のレスポンスの"data"に2回目以降のレスポンスの"data"を末尾に追加する。

        Returns:
            dict: APIから取得したプロジェクトメタデータを返す。11件以上の場合は以下の形式になる。
                - "data": 登録されているすべてのプロジェクトメタデータが含まれる。
                - "links": 1ページ目の情報が入っている。
                - "meta": 1ページ目の情報が入っている。

        Raises:
            UnauthorizedError:認証処理を実行せずに実行した場合のエラー
            APIError:APIのサーバーエラー、タイムアウト、リクエスト回数の上限
        """
        if not self._is_authenticated:
            logger.error(f"Executed without authentication process")
            raise UnauthorizedError("認証されていません")
        base_url = self._config_file["url"]["project_metadata"]
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

    def get_file_metadata(self) -> dict:
        """ファイルメタデータを取得するメソッドです。

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

    def get_project_info(self) -> dict:
        """プロジェクト情報を取得するメソッドです。

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

    def get_member_info(self) -> dict:
        """メンバー情報を取得するメソッドです。

        メンバーが11人以上の場合は1回目のレスポンスの"data"に2回目以降のレスポンスの"data"を末尾に追加する。

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
