"""エラーのモジュールです。"""

class NotFoundMappingDefinitionError(Exception):
    """マッピング定義ファイルが見つからないエラーのクラスです。"""

class MetadataTypeError(Exception):
    """データの型が間違っているエラーのクラスです。"""

class NotFoundKeyError(Exception):
    """キーが見つからない場合のエラークラスです。"""

class MappingDefinitionError(Exception):
    """マッピング定義に誤りがある場合のエラークラスです。"""

class DataFormatError(Exception):
    """データの形式に問題がある場合のエラーです。"""
