import pickle
import os
import pandas as pd
import json


def load_json(filepath: str) -> dict:
    """
    jsonファイルを読み込み辞書形式で返す。

    parameter
    -------
        filepath (str): 読み込むjsonファイル

    return
    -------
        jsonファイルの中身（辞書）
    """

    if not os.path.exists(filepath):
        raise Exception(f"The file {filepath} was not found")

    if not filepath.endswith(".json"):
        raise Exception(
            "The file is " + filepath.split(".")[-1] + "file, not json (.json) file"
        )

    return json.load(open(filepath, "r"))


def save_as_pickle(data: object, filePath: str, overwrite: bool = False) -> None:
    """任意のクラスオブジェクトをpickle形式で保存する。

    parameter
    ---------
        data: 保存されるクラスオブジェクト
        filePath: 保存先のファイル
        overwrite (default): True (既にファイルがあっても上書きする。) or False(上書きしない)

    return
    ------
        None

    :exception:
        拡張子がpkl以外の場合、例外を投げる。

    """

    os.makedirs("/".join(filePath.replace("\\", "/").split("/")[:-1]), exist_ok=True)

    if (not overwrite) and (os.path.exists(filePath)):
        raise Exception("The file already exists\n" + filePath)
    else:
        pickle.dump(data, open(filePath, "wb"))


def load_pickle(file_path: str) -> object:
    """pickle形式のファイルを読み込む

    :pram:
        file_path: 読み込むファイル

    :return:
        該当ファイルで保存されたクラスオブジェクト

    """

    if not os.path.exists(file_path):
        raise Exception("There is no such a file")

    if not file_path.endswith(".pkl"):
        raise Exception(
            "The file is ." + file_path.split(".")[-1] + "file, not pickle (.pkl) file"
        )

    return pickle.load(open(file_path, "rb"))


def save_as_csv(data: dict, filePath: str, overwrite: bool = False) -> None:
    """pandas.DataFramのオブジェクトをcsv形式で保存する。

    :param:
        data: DataFrame
        filePath: 保存先のファイル
        overwrite (default False): True (既にファイルがあっても上書きする。) or False(上書きしない)

    :return:
        None

    :exception:
        拡張子がcsv以外の場合、例外を投げる。

    """

    os.makedirs("/".join(filePath.replace("\\", "/").split("/")[:-1]), exist_ok=True)

    if not filePath.endswith(".csv"):
        raise Exception("The file is " + filePath.split(".")[-1] + ", not csv file")

    if (not overwrite) and os.path.exists(filePath):
        raise Exception("The file already exists\n" + filePath)

    if isinstance(data, pd.core.frame.DataFrame):
        data.to_csv(filePath, index=False)
    else:
        raise Exception(f"cannot save as csv format because of data type {type(data)}")


def save_data_as_csv_and_pkl(
    data: pd.DataFrame, filePath: str, overwrite: bool = False
) -> None:

    """
        自作したデータをpklファイルとcsvファイルで保存するスクリプト

     args:
        data: ファイル出力するデータ
        filePath: ファイル名（絶対パス推奨。最後は必ずピリオドで終了すること）
        ovewwrite: 上書きするか (True: すでにファイルがあっても保存。Falseなら、すでにファイルがあれば例外)

    Returns:
        None

    Exception:
        filepathの後ろがピリオドで終わらない場合
    """

    if not filePath.endswith("."):
        raise Exception("filePath must be end with .")

    save_as_pickle(data, filePath + "pkl", overwrite)
    save_as_csv(data, filePath + "csv", overwrite)