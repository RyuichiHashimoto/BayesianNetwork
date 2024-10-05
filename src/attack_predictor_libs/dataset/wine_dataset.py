import polars as pl
from sklearn.datasets import load_wine
import os
from attack_predictor_libs.dataset.dataset import Dataset
import pandas as pd
from sklearn.preprocessing import StandardScaler
CACHE_POSTFIX = ".cache.pkl"

class WineDataset(Dataset):
    
    def __getitem__(self, key):
        raise NotImplementedError
        
    def _load_file(self, filepath: str) -> pl.DataFrame:
        dirname = os.path.dirname("/home/work/dataset/wine/wine.csv")
        os.makedirs(dirname, exist_ok=True)                         
        wine = load_wine()
        df = pd.DataFrame(wine.data, columns=wine.feature_names) # Explanatory variable        
        df['Wine Class'] = wine.target # Objective variable

        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df)
        df =pd.DataFrame(df_scaled,columns=df.columns)

        return pl.from_pandas(df)
    


        
if __name__ == "__main__":
    wine = WineDataset("/home/work/dataset/wine/wine.csv")
    print(wine.data)