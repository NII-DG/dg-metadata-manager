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
        "filter-file1.json": ["name"],
        "filter-file2.json": {"name": None},
        "filter-file3.json": ["dummy"]
    }

    # ファイル作成
    for path, contents in files.items():
        with open(path, 'w') as f:
            json.dump(contents, f)

    yield

    # ファイル削除
    for path in files.keys():
        os.remove(path)


def exe_cmd(cmd):
    child = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    rt = child.returncode
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    return stdout, stderr, rt


def test_main_success_1():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage",
           "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_2():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter", "name"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_3():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token",
           f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter", "researcher[].email[]"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_4():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM",
           "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter", "name"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_5():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token",
           f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter", "name", "description"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_6(create_dummy_filter_files):
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token",
           f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter-file", "filter-file1.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_7(create_dummy_filter_files):
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token",
           f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter", "description", "--filter-file", "filter-file1.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0


def test_main_success_8(tmp_path):
    output_path = tmp_path / " output1.json"
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token",
           f"{grdm_token}", "--id", f"{grdm_project_id}", "--file", f"{output_path}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0
    assert out == ""
    with open(output_path) as f:
        result = json.load(f)


def test_main_success_9():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token",
           f"{grdm_token}", "--id", f"{grdm_project_id}", "--project-metadata-id", f"{grdm_project_metadata_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 0

def test_main_failure_1():
    cmd = ["metadatamanager", "get", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: the following arguments are required: --schema" in err

def test_main_failure_2():
    cmd = ["metadatamanager", "get", "--schema", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: argument --schema: expected one argument" in err

def test_main_failure_3():
    cmd = ["metadatamanager", "get", "--schema", "dummy", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: マッピング定義ファイルが見つかりません。" in err

def test_main_failure_4():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: the following arguments are required: --storage" in err

def test_main_failure_5():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: argument --storage: expected one argument" in err

def test_main_failure_6():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "dummy", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: 対応していないストレージが指定されました" in err

def test_main_failure_7():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: 認証に失敗しました" in err

def test_main_failure_8():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: argument --token: expected one argument" in err

def test_main_failure_9():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: 認証に失敗しました" in err

def test_main_failure_10():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_access_denied_token}", "--id", f"{grdm_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "エラーが発生しました: 認証に失敗しました" in err

def test_main_failure_11():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: プロジェクトが存在しません" in err

def test_main_failure_12():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: argument --id: expected one argument" in err

def test_main_failure_13():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", "dummy"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: プロジェクトが存在しません" in err

def test_main_failure_14():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_access_denied_project_id}"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: プロジェクトへのアクセス権がありません" in err

def test_main_failure_15():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: argument --filter: expected one argument" in err

def test_main_failure_16():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter", "dummy"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: 指定したプロパティ: dummy が存在しません" in err

def test_main_failure_17():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter-file"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 2
    assert "metadatamanager get: error: argument --filter-file: expected one argument" in err

def test_main_failure_18():
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter-file", "dummy.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
    assert "エラーが発生しました: ファイルが見つかりません: 'dummy.json'" in err

def test_main_failure_19(create_dummy_filter_files):
    cmd = ["metadatamanager", "get", "--schema", "RF", "--storage", "GRDM", "--token", f"{grdm_token}", "--id", f"{grdm_project_id}", "--filter-file", "filter-file2.json"]
    out, err, rt = exe_cmd(cmd)

    assert rt == 1
