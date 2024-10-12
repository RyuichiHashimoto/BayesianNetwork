import polars as pl
import os
from abc import ABC, abstractmethod
from common_libs.fileio import load_pickle, save_as_pickle
from attack_predictor_libs._exception import AttackLibException
import logging
import pandas as pd
logger = logging.getLogger(__name__)

CACHE_POSTFIX = ".cache.pkl"

class Dataset(ABC):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._data = None
        self._data_as_pandas = None
        
        self._load(filepath)
        
    
    @property
    def data(self) -> pl.DataFrame:
        if self._data is None:
            raise AttackLibException("Dataset is not loaded yet")
    
        return self._data
    
    @property
    def data_as_pandas(self) -> pd.DataFrame:
        if self._data is None:
            raise AttackLibException("Dataset is not loaded yet")
        
        if self._data_as_pandas is not None:
            return self._data_as_pandas
        
        self._data_as_pandas = self._data.to_pandas()
        return self._data_as_pandas


    
    def _load(self, filepath: str, create_cache: bool = True) -> pl.DataFrame:
        if self._has_cache(filepath):
            logger.info(f"load cache file from: {filepath}")
            self._data = self._load_cache(filepath)
        else:
            self._data = self._load_file(filepath)
            if create_cache:
                logger.info(f"save cache file to: {filepath}")
                self._save_cache(self._data, filepath)
        
    
    # @abstractmethod
    # def __getitem__(self, index: str):
    #     raise NotImplementedError
        
    @abstractmethod
    def _load_file(self, filepath: str) -> pl.DataFrame:
        raise NotImplementedError
    
    def _craete_cachepath(self, filepath: str):
        return filepath + CACHE_POSTFIX
    
    def _has_cache(self, filepath: str):
        return os.path.exists(self._craete_cachepath(filepath))
    
    def _load_cache(self, filepath: str):
        return load_pickle(self._craete_cachepath(filepath))
        
    def _save_cache(self, data: any, filepath: str):
        save_as_pickle(data, self._craete_cachepath(filepath))
        if isinstance(self._data, pl.DataFrame):
            self._data.write_csv(filepath + ".csv")


        
    