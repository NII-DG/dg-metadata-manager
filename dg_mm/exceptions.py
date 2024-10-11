"""エラーのモジュールです。"""

class NotFoundMappingDefinitionError(Exception):
    """マッピング定義ファイルが見つからないエラーのクラスです。"""

class MetadataTypeError(Exception):
    """データの型が間違っているエラーのクラスです。"""

class NotFoundKeyError(Exception):
    """キーが見つからない場合のエラークラスです。"""

class MappingDefinitionError(Exception):
    """マッピング定義に誤りがある場合のエラークラスです。"""

class NotFoundSourceError(Exception):
    """メタデータの取得先を特定できなかった場合のエラークラスです。"""
