import argparse
import json
import sys
import traceback

from dg_mm.models.metadata_manager import MetadataManger
from dg_mm.exceptions import MetadatamanagerError


def main():
    """コマンドラインインタフェースのエントリーポイント"""
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    parser_get = subparser.add_parser('get', help='GRDMを含む研究データ管理サービスからメタデータを収集し、RDC-AP/DG-APの定義に則った形式で取得する。')
    parser_get.add_argument('--schema', required=True, help='スキーマの名称を指定する')
    parser_get.add_argument('--storage', required=True, help='ストレージの名称を指定する')
    parser_get.add_argument(
        '--token', help='ストレージ認証に使用するトークンを指定する。storageにGRDMを指定した場合に必要です。')
    parser_get.add_argument(
        '--id', help='ストレージ内の情報を一意に特定するためのID。storageにGRDMを指定した場合に必要です。')
    parser_get.add_argument(
        '--filter', nargs='*', help='スキーマの一部を指定したい場合に使用する。スキーマのプロパティを、ルートから「.」でつなげた形式で指定する。複数指定可能。')
    parser_get.add_argument(
        '--filter-file', dest='filter_file',
        help='スキーマの一部をファイルとして指定したい場合に使用する。スキーマのプロパティ一覧が書かれたjsonファイルのパスを指定する。filterと同時に指定した場合はこちらを優先する。')
    parser_get.add_argument(
        '--file', help='ファイル出力先。通常は標準出力に出力されるメタデータをファイルに出力したい場合に使用する。既に存在するファイルには上書きする。')
    parser_get.set_defaults(func=get_metadata)

    try:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except MetadatamanagerError as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        return 1
    else:
        return 0


def get_metadata(args: argparse.Namespace):
    """メタデータ取得機能を実行するメソッドです。

    Args:
        args (argparse.Namespace): コマンドライン引数
    """
    if args.filter_file is not None:
        with open(args.filter_file, 'r') as f:
            args.filter = json.load(f)
    params = {
        'schema': args.schema,
        'storage': args.storage,
        'token': args.token,
        'id': args.id,
        'option': args.filter
    }
    mm = MetadataManger()
    result = mm.get_metadata(**params)
    if args.file is not None:
        with open(args.file, 'w') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    else:
        print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()
