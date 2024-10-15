import polars as pl
import os
from attack_predictor_libs.dataset.dataset import Dataset
from attack_predictor_libs.mitre.mitre import PREPARATION_DICT, INTRUSION_DICT, COMPROMISE_DICT
from logging import getLogger


logger = getLogger(__name__)
CACHE_POSTFIX = ".cache.pkl"

class GuideDataset(Dataset):
    
    def __init__(self, filepath: str = "/home/work/dataset/guide/guide.csv"):
        return super().__init__(filepath)
    
    def __getitem__(self, key: tuple[str, int]) -> pl.DataFrame:
        mode, idx = key
        if mode not in ["train", "test"]:
            raise KeyError(f"mode must be 'train' or 'test', but got {mode}")
        
        condition = (pl.col("dataset_type") == mode) & (pl.col("IncidentId") == idx)
        ret_df = self._data.filter(condition)

        if ret_df.shape[0] == 0:
            raise KeyError(f"mode = {mode} and idx = {idx} is not found")
        
        return ret_df.sort("Timestamp")
        
        # raise NotImplementedError
        
    def _load_file(self, filepath: str) -> pl.DataFrame:
        train_path =  "/home/work/dataset/guide/GUIDE_Train.csv"
        test_path = "/home/work/dataset/guide/GUIDE_Test.csv"

        if not os.path.exists(train_path):            
            raise FileNotFoundError(f"File not found: {train_path}")
        
        if not os.path.exists(test_path):            
            raise FileNotFoundError(f"File not found: {test_path}")

        
        train_df = pl.read_csv(train_path)
        test_df = pl.read_csv(test_path)
        test_df = test_df.drop("Usage")

        train_df = train_df.with_columns(pl.col("EmailClusterId").cast(str))
        test_df = test_df.with_columns(pl.col("EmailClusterId").cast(str))
        logger.warning("EmailClusterId is casted to str")
        
        train_df = train_df.with_columns(pl.lit("train").alias("dataset_type"))        
        test_df = test_df.with_columns(pl.lit("test").alias("dataset_type"))
        df = pl.concat([train_df, test_df])

        df = df.drop_nulls(subset=["MitreTechniques"])
        
        df = df.with_columns(
            pl.col('MitreTechniques').map_elements(lambda x: check_contains_preparation(x, PREPARATION_DICT), return_dtype=bool).alias('is_preparation_alert')
        )
        df = df.with_columns(
            pl.col('MitreTechniques').map_elements(lambda x: check_contains_preparation(x, INTRUSION_DICT), return_dtype=bool).alias('is_intrusion_alert')
        )
        df = df.with_columns(
            pl.col('MitreTechniques').map_elements(lambda x: check_contains_preparation(x, COMPROMISE_DICT), return_dtype=bool).alias('is_compromise_alert')
        )

        df =  df.with_columns(    (
            (pl.col("is_preparation_alert").cast(int) *(2**0)) +  # is_preparation_alert をビット2にシフト
            (pl.col("is_intrusion_alert").cast(int) *(2**1)) +   # is_intrusion_alert をビット1にシフト
            pl.col("is_compromise_alert").cast(int)  *(2**2)           # is_compromise_alert をビット0に
        ).alias("alert_bit_value"))


        if len(PREPARATION_DICT) == 0:
            logger.warning("preparation_dict is empty")
        if len(INTRUSION_DICT) == 0:
            logger.warning("intrusion+_dict is empty")
        if len(COMPROMISE_DICT) == 0:
            logger.warning("compromize_dict is empty")

        
        df = df.with_columns(pl.col("Timestamp").cast(pl.Datetime))
        logger.warning("Timestamp is casted as pl.Datetime")
        return df
    
def check_contains_preparation(techniques, preparation_dict, delimiter: str = ";"):
    """ GUIDEdatasetの特徴量の前処理の有無を確認する関数"""
    # mitreTechniques を ';' で分割してリスト化
    techniques_list = techniques.split(delimiter)
    # それぞれのテクニックが辞書にあり、かつTrueであればTrueを返す

    return any(preparation_dict.get(technique, False) for technique in techniques_list)

        
if __name__ == "__main__":
    wine = GuideDataset("/home/work/dataset/guide/wine.csv")
    print(wine.data)