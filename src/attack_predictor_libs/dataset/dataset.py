import polars as pl
import os
from abc import ABC, abstractmethod
from common_libs.fileio import load_pickle, save_as_pickle
from attack_predictor_libs._exception import AttackLibException
import logging

logger = logging.getLogger(__name__)

CACHE_POSTFIX = ".cache.pkl"

class Dataset(ABC):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._load(filepath)
        
    
    @property
    def data(self):
        if self._data is None:
            raise AttackLibException("Dataset is not loaded yet")
        
        return self._data
    
    def _load(self, filepath: str, create_cache: bool = True) -> pl.DataFrame:
        if self._has_cache(filepath):
            return self._load_cache(filepath)
        else:
            logger.info(f"Cache file not found: {filepath}")
            self._data = self._load_file(filepath)
            if create_cache:
                self._save_cache(self._data, filepath)

    
    @abstractmethod
    def __getitem__(self, index: str):
        raise NotImplementedError
        
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
        return save_as_pickle(data, self._craete_cachepath(filepath))
    