"""エラーのモジュールです。"""


class MetadatamanagerError(Exception):
    """MetadataManagerのエラークラスです。"""
    pass


class MappingDefinitionNotFoundError(MetadatamanagerError):
    """マッピング定義ファイルが見つからない場合のエラークラスです。"""
    pass


class DataTypeError(MetadatamanagerError):
    """データの型が間違っている場合のエラークラスです。"""
    pass


class KeyNotFoundError(MetadatamanagerError):
    """キーが見つからない場合のエラークラスです。"""
    pass


class MappingDefinitionError(MetadatamanagerError):
    """マッピング定義に誤りがある場合のエラークラスです。"""
    pass


class DataFormatError(MetadatamanagerError):
    """データの形式に問題がある場合のエラークラスです。"""
    pass


class APIError(MetadatamanagerError):
    """APIのエラークラスです。"""
    pass


class UnauthorizedError(MetadatamanagerError):
    """未認証の場合のエラークラスです。"""
    pass


class AccessDeniedError(MetadatamanagerError):
    """アクセス権限がない場合のエラークラスです。"""
    pass


class InvalidSchemaError(MetadatamanagerError):
    """スキーマ不正の場合のエラークラスです。"""
    pass


class InvalidStorageError(MetadatamanagerError):
    """ストレージ不正の場合のエラークラスです。"""
    pass


class InvalidTokenError(MetadatamanagerError):
    """トークン不正の場合のエラークラスです。"""
    pass


class InvalidIdError(MetadatamanagerError):
    """ID不正の場合のエラークラスです。"""
    pass


class MetadataNotFoundError(MetadatamanagerError):
    """メタデータが見つからなかった場合のエラークラスです。"""
    pass
