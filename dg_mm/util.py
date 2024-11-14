import configparser
import json
import pathlib


class PackageFileReader():
    """パッケージ内のファイルの読み込み処理をまとめたクラスです。"""

    @classmethod
    def is_file(cls, relative_path: str) -> bool:
        """ファイルの存在チェックを行うメソッドです。

        Args:
            relative_path (str): ファイルパス(dg_mmフォルダからの相対パス)

        Returns:
            bool: ファイルが存在する場合はTrue
        """
        file_path = cls._get_absolute_path(relative_path)
        return file_path.is_file()

    @classmethod
    def read_json(cls, relative_path: str, encoding: str = None) -> dict:
        """JSONファイルを読み込むメソッドです。

        Args:
            relative_path (str): ファイルパス(dg_mmフォルダからの相対パス)
            encoding (str): 文字エンコード

        Returns:
            dict: jsonから変換したPythonオブジェクト
        """

        file_path = cls._get_absolute_path(relative_path)
        with open(file_path, mode='r', encoding=encoding) as f:
            return json.load(f)

    @classmethod
    def read_ini(cls, relative_path: str) -> configparser.ConfigParser:
        """iniファイルを読み込むメソッドです。

        Args:
            relative_path (str): ファイルパス(dg_mmフォルダからの相対パス)

        Returns:
            ConfigParser: 設定ファイルのパーサー
        """

        file_path = cls._get_absolute_path(relative_path)
        ini_file = configparser.ConfigParser()
        ini_file.read(file_path)
        return ini_file

    @classmethod
    def _get_absolute_path(cls, relative_path: str) -> pathlib.Path:
        """ファイルの絶対パスを取得するメソッドです。

        Args:
            relative_path (str): ファイルパス(dg_mmフォルダからの相対パス)

        Returns:
            pathlib.Path: 絶対パス
        """

        package_path = pathlib.Path(__file__).resolve().parent
        file_path = package_path.joinpath(relative_path)
        return file_path
