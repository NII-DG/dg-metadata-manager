"""エラーのモジュールです。"""


class MetadatamanagerError(Exception):
    """MetadataManagerのエラー"""
    pass


class NotFoundMappingDefinitionError(MetadatamanagerError):
    """マッピング定義ファイルが見つからないエラーのクラスです。"""
    pass


class MetadataTypeError(MetadatamanagerError):
    """データの型が間違っているエラーのクラスです。"""
    pass


class NotFoundKeyError(MetadatamanagerError):
    """キーが見つからない場合のエラークラスです。"""
    pass


class MappingDefinitionError(MetadatamanagerError):
    """マッピング定義に誤りがある場合のエラークラスです。"""
    pass


class DataFormatError(MetadatamanagerError):
    """データの形式に問題がある場合のエラーです。"""
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


class InvalidIdError(MetadatamanagerError):
    """ID不正の場合のエラー"""
    pass


class InvalidStorageError(MetadatamanagerError):
    """対応していないストレージを指定した場合のエラー"""
    pass


class MetadataNotFoundError(MetadatamanagerError):
    """メタデータが見つからなかった場合のエラー"""
    pass
