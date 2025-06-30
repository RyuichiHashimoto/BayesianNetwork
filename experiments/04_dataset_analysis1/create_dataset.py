import pandas as pd
from pathlib import Path
from tqdm import tqdm
import os
from glob import glob
import matplotlib.pyplot as plt
import json

def extract_and_export(input_csv: str, output_root: str = 'output'):
    # CSV 読み込み（Timestamp を datetime 型にパース）
    df = pd.read_csv(input_csv, parse_dates=['Timestamp'])

    # フィルタ条件
    mask_grade = df['IncidentGrade'] == 'TruePositive'
    mask_mitre = (
        df['MitreTechniques'].notna() &
        df['MitreTechniques'].str.strip().ne('')
    )

    # 抽出＆ソート
    filtered = df[mask_grade & mask_mitre]    

    # グルーピング＆ファイル出力
    grouped = filtered.groupby(['OrgId', 'IncidentId'])
    for (org_id, incident_id), group in tqdm(grouped):
        # 出力先ディレクトリを組み立て
        dir_path = Path(output_root) / str(org_id) / str(incident_id)
        dir_path.mkdir(parents=True, exist_ok=True)

        # CSV として保存
        out_file = dir_path / 'events.csv'
        group.sort_values("Timestamp")
        group.to_csv(out_file, index=False)

    print(f"Completed exporting {len(grouped)} groups to “{output_root}/”")


def max_consecutive_same(series: pd.Series) -> int:
    """
    シリーズ中の非空文字列について、
    同じ文字列が連続する最長の長さを返す。
    NaN または空白文字列があった場合は ValueError を投げる。
    """
    max_run = 0
    current_run = 0
    prev_val = None

    for idx, raw in enumerate(series):
        # NaN チェック
        if pd.isna(raw):
            raise ValueError(f"Row {idx}: Encountered NaN in MitreTechniques")
        # 文字列に変換して前後空白削除
        val = str(raw).strip()
        # 空白文字列チェック
        if val == "":
            raise ValueError(f"Row {idx}: Encountered blank MitreTechniques")
        
        if val == prev_val:
            # 連続中
            current_run += 1
        else:
            # 新しい値に切り替え
            current_run = 1
            prev_val = val

        if current_run > max_run:
            max_run = current_run

    return max_run


def compute_ratios(root_dir='output'):
    """
    output/{OrgID}/{IncidentID}/events.csv を再帰的に探索し、
    各ファイルの (最大連続MitreTechniques文字列行数)/(総行数) を計算してリストで返す。
    """
    ratios = []
    
    for org in os.listdir(root_dir):
        org_path = os.path.join(root_dir, org)
        if not os.path.isdir(org_path):
            continue
        for incident in os.listdir(org_path):
            csv_path = os.path.join(org_path, incident, 'events.csv')
            if not os.path.isfile(csv_path):
                continue

            df = pd.read_csv(csv_path, parse_dates=['Timestamp'])

            # MitreTechniques が文字列として非空かどうか
            mask = df['MitreTechniques']
            total = len(df)
            

            max_run = max_consecutive_same(mask)
            ratio = max_run / total
            ratios.append(ratio)
            print(f"{org}/{incident}: max_run={max_run}, total={total}, ratio={ratio:.3f}")

    return ratios

def compute_and_print_max_runs(root_dir: str = 'output'):
    """
    output 以下を再帰探索し、各 events.csv ごとに
    max_consecutive_same を計算してプリントする。
    """
    for org in os.listdir(root_dir):
        org_path = os.path.join(root_dir, org)
        if not os.path.isdir(org_path):
            continue
        for incident in os.listdir(org_path):
            csv_path = os.path.join(org_path, incident, 'events.csv')
            if not os.path.isfile(csv_path):
                continue

            df = pd.read_csv(csv_path)
            max_run = max_consecutive_same(df['MitreTechniques'])
            print(f"{org}/{incident}: 最長連続長 = {max_run} レコード")



def normalize_mitre(tech):
    """
    MITRETechnique 文字列を
    - 'T4124.352'         → 'T4124'
    - 'T4124.352;T325.1'  → 'T4124;T325'
    とする。
    """
    if pd.isna(tech):
        return tech  # NaN はそのまま
    parts = str(tech).split(';')
    normalized = []
    for p in parts:
        p = p.strip()
        # ドットで分割し、最初の要素を取る
        first = p.split('.', 1)[0]
        normalized.append(first)
    return ';'.join(normalized)


def plot_histogram(ratios, bins=10, save_path=None):
    """
    割合リストのヒストグラムをプロット
    """
    plt.figure(figsize=(8, 5))
    plt.hist(ratios, bins=bins)
    plt.xlabel('Max Consecutive MitreTechniques Ratio')
    plt.ylabel('Number of Files')
    plt.title('Histogram of Max Consecutive MitreTechniques Ratios')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Saved histogram to {save_path}")
    else:
        plt.show()


def remove_consecutive_duplicates(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    df[col] で同じ文字列が連続している場合、２つ目以降を削除する。
    例:
      A
      A
      B
      B
      A  →  A, B, A
    """
    # Series.shift() で１行前と比較し、異なる行だけ残す
    mask = df[col].ne(df[col].shift())
    return df[mask].reset_index(drop=True)


def preprocess_and_export(input_dir: str, mode: str = "train"):
    FILES = glob(f"{input_dir}/**/events.csv", recursive=True)
    for file in tqdm(FILES):
        df = pd.read_csv(file)
        df['MitreTechniques'] = df['MitreTechniques'].apply(normalize_mitre) ## subtechnique -> technique
        df_clean = remove_consecutive_duplicates(df, "MitreTechniques") ## 連続で出現するTechnique集合を一つにまとめる。
        df_clean.to_csv(file.replace("events.csv", "preprocessed-events.csv"), index=False)

def export_scenario(input_dir: str, mode: str = "train"):
    FILES = glob(f"{input_dir}/**/preprocessed-events.csv", recursive=True)
    for file in tqdm(FILES):
        df = pd.read_csv(file)
        if len(df) >= 5:
            scenario = {
                "scenario": df['MitreTechniques'].astype(str).tolist()
            }
            json_path = file.replace("preprocessed-events.csv", "scenario.json")
            org_id = file.split("/")[-3]
            incident_id = file.split("/")[-2]
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(scenario, f, ensure_ascii=False, indent=2)
                print(f"[{org_id}/{incident_id}] scenario.json を出力 ({len(df)} レコード)")
        else:
            output_path = file.replace("preprocessed-events.csv", "scenario_not_created.txt")
            with open(output_path, "w") as fout:
                pass 


if __name__ == '__main__':
    
    #
    mode = "train"
    
    # データ抽出
    # extract_and_export(output_root=f"output/{mode}", input_csv=f'/home/work/dataset/guide/GUIDE_{mode}.csv')

    # データ加工
    # preprocess_and_export(f"output/{mode}", mode)

    # to_json()
    export_scenario(f"output/{mode}", mode)

    

    
    
        

    


    
    
    
    
    # ratios = compute_ratios(root_dir='output/train')
    # plot_histogram(ratios, bins=100, save_path='mitre_ratio_histogram.png')



    # extract_and_export('/home/work/dataset/guide/train-sumple.csv')
    