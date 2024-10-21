"""エラーのモジュールです。"""

class NotFoundMappingDefinitionError(Exception):
    """マッピング定義ファイルが見つからないエラーのクラスです。"""
    pass

class MetadataTypeError(Exception):
    """データの型が間違っているエラーのクラスです。"""
    pass


class NotFoundKeyError(Exception):
    """キーが見つからない場合のエラークラスです。"""
    pass


class MappingDefinitionError(Exception):
    """マッピング定義に誤りがある場合のエラークラスです。"""
    pass


class DataFormatError(Exception):
    """データの形式に問題がある場合のエラーです。"""
    pass


class MetadatamanagerError(Exception):
    """MetadataManagerのエラー"""
    pass


class APIError(MetadatamanagerError):
    """APIのエラー"""
    pass


class UnauthorizedError(MetadatamanagerError):
    """未認証のエラー"""
    pass


class AccessDeniedError(MetadatamanagerError):
    """アクセス権限がない場合のエラー"""
    pass


class InvalidTokenError(MetadatamanagerError):
    """トークン不正の場合のエラー"""
    pass


class InvalidProjectError(MetadatamanagerError):
    """プロジェクト不正の場合のエラー"""
    pass


class InvalidStorageError(MetadatamanagerError):
    """対応していないストレージを指定した場合のエラー"""
    pass

class MetadataNotFoundError(MetadatamanagerError):
    """指定されたタイトルのプロジェクトメタデータが見つからなかった場合のエラー"""
    pass
