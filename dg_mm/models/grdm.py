"""GRDMストレージに関するモジュールです。"""

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

    def get_project_info(self)-> dict:
        """プロジェクト情報を取得するメソッドです。"""

    def get_member_info(self)-> dict:
        """メンバー情報を取得するメソッドです。"""
