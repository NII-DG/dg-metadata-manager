import json
import os
import subprocess

import pytest

grdm_token = os.environ['GRDM_TOKEN']
grdm_project_id = os.environ['GRDM_PROJECT_ID']
grdm_project_metadata_id = os.environ['GRDM_PROJECT_METADATA_ID']
grdm_access_denied_token = os.environ['GRDM_ACCESS_DENIED_TOKEN']
grdm_access_denied_project_id = os.environ['GRDM_ACCESS_DENIED_PROJECT_ID']


@pytest.fixture
def create_dummy_filter_files():
    files = {
        "filter-file1.json": '["name"]',
        "filter-file2.json": 'name',
        "filter-file3.json": '["dummy"]',
    }

    # ファイル作成
    for path, contents in files.items():
        with open(path, 'w') as f:
            f.write(contents)

    yield

    # ファイル削除
    for path in files.keys():
        os.remove(path)


@pytest.fixture
def create_dummy_output_files():
    files = {
        "output2.json": '{"name":"project name"}',
    }

    # ファイル作成
    for path, contents in files.items():
        with open(path, 'w') as f:
            f.write(contents)

    # 書き込み権限がないフォルダ作成
    dir = "no_access"
    os.makedirs(dir)
    os.chmod(dir, 0o444)

    yield

    # ファイル削除
    for path in files.keys():
        os.remove(path)

    # フォルダ削除
    os.rmdir(dir)


def exe_cmd(cmd):
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    rt = child.returncode
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    return stdout, stderr, rt


def test_main_success_1():
    """スキーマ全体を取得"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_2():
    """スキーマの一部(葉ノード)を取得"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter", "name"]
    out, err, rt = exe_cmd(cmd)
    print(out)

    assert rt == 0


def test_main_success_3():
    """スキーマの一部(内部ノード)を取得"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter", "researcher[].email[]"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_4():
    """フィルタのオプションを指定して、プロパティを1つ入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter", "name"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_5():
    """フィルタのオプションを指定して、プロパティを2つ入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter", "name", "description"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_6(create_dummy_filter_files):
    """フィルタファイルのオプションを指定"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter-file", "filter-file1.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_7(create_dummy_filter_files):
    """フィルタとフィルタファイルのオプションを両方指定(フィルタファイルが優先される)"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter", "description", "--filter-file", "filter-file1.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_8(tmp_path):
    """ファイル出力先のオプションを指定"""

    output_path = tmp_path / " output1.json"
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--file", output_path]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0
    assert out == ""
    with open(output_path) as f:
        result = json.load(f)   # JSONファイルとして読み込めればOK


def test_main_success_9():
    """プロジェクトメタデータIDのオプションを指定"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--project-metadata-id", grdm_project_metadata_id]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_failure_1():
    """スキーマのオプションを指定しない"""

    cmd = ["metadatamanager", "get", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: the following arguments are required: --schema" in err


def test_main_failure_2():
    """スキーマのオプションを指定したが、スキーマ名を入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "--storage", "GRDM",
           "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --schema: expected one argument" in err


def test_main_failure_3():
    """スキーマのオプションを指定して、存在しないスキーマ名を入力"""

    cmd = ["metadatamanager", "get", "--schema", "dummy", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: マッピング定義ファイルが見つかりません。" in err


def test_main_failure_4():
    """ストレージのオプションを指定しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF",
           "--token", grdm_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: the following arguments are required: --storage" in err


def test_main_failure_5():
    """ストレージのオプションを指定したが、ストレージ名を入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage",
           "--token", grdm_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --storage: expected one argument" in err


def test_main_failure_6():
    """ストレージのオプションを指定して、存在しないストレージ名を入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "dummy",
           "--token", grdm_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: 対応していないストレージが指定されました" in err


def test_main_failure_7():
    """ストレージにGRDMを入力したが、トークンのオプションを指定しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: 認証に失敗しました" in err


def test_main_failure_8():
    """トークンのオプションを指定したが、トークンを入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --token: expected one argument" in err


def test_main_failure_9():
    """トークンのオプションを指定して、存在しないトークンを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", "dummy", "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: 認証に失敗しました" in err


def test_main_failure_10():
    """トークンのオプションを指定して、アクセス権限がないトークンを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_access_denied_token, "--id", grdm_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: トークンのアクセス権が不足しています" in err


def test_main_failure_11():
    """ストレージにGRDMを入力したが、IDのオプションを指定しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: プロジェクトが存在しません" in err


def test_main_failure_12():
    """IDのオプションを指定したが、GRDMのプロジェクトIDを入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --id: expected one argument" in err


def test_main_failure_13():
    """IDのオプションを指定して、存在しないGRDMのプロジェクトIDを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", "dummy"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: プロジェクトが存在しません" in err


def test_main_failure_14():
    """IDのオプションを指定して、トークン発行したユーザーにアクセス権限がないGRDMのプロジェクトIDを指定"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_access_denied_project_id]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: プロジェクトへのアクセス権がありません" in err


def test_main_failure_15():
    """フィルタのオプションを指定したが、スキーマのプロパティを入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: 絞り込むプロパティが指定されていません。" in err


def test_main_failure_16():
    """フィルタのオプションを指定して、スキーマに存在しないプロパティを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter", "dummy"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: 指定したプロパティ: dummy が存在しません" in err


def test_main_failure_17():
    """フィルタファイルのオプションを指定したが、ファイルパスを入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter-file"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --filter-file: expected one argument" in err


def test_main_failure_18():
    """フィルタファイルのオプションを指定して、存在しないファイルのパスを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter-file", "dummy.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: ファイルが見つかりません: 'dummy.json'" in err


def test_main_failure_19(create_dummy_filter_files):
    """フィルタファイルのオプションを指定して、期待するフォーマットではないファイルのパスを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter-file", "filter-file2.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: フィルタファイルのフォーマットに誤りがあります" in err


def test_main_failure_20(create_dummy_filter_files):
    """フィルタファイルのオプションを指定して、スキーマに存在しないプロパティが書かれたファイルのパスを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--filter-file", "filter-file3.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: 指定したプロパティ: ['dummy'] が存在しません" in err


def test_main_failure_22():
    """ファイル出力先のオプションを指定したが、ファイルパスを入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--file"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --file: expected one argument" in err


def test_main_failure_23(create_dummy_output_files):
    """ファイル出力先のオプションを指定して、すでにファイルが存在するパスを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--file", "output2.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: The file 'output2.json' already exists" in err


def test_main_failure_24(create_dummy_output_files):
    """ファイル出力先のオプションを指定して、存在しないフォルダを含むパスを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--file", "dummy/output3.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "エラーが発生しました: The directory 'dummy' does not exist." in err


def test_main_failure_25(create_dummy_output_files):
    """ファイル出力先のオプションを指定して、書き込み権限がないフォルダを含むパスを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--file", "no_access/output4.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "Permission denied: 'no_access/output4.json'" in err


def test_main_failure_26():
    """プロジェクトメタデータIDのオプションを指定したが、IDを入力しない"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--project-metadata-id"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --project-metadata-id: expected one argument" in err


def test_main_failure_27():
    """プロジェクトメタデータIDのオプションを指定して、存在しないプロジェクトメタデータIDを入力"""

    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", grdm_token, "--id", grdm_project_id,
           "--project-metadata-id", "dummy"]
    out, err, rt = exe_cmd(cmd)

    assert rt != 0
    assert "metadatamanager get: error: argument --project-metadata-id: expected one argument" in err
