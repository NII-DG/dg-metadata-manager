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
