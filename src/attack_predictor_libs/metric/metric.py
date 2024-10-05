from abc import ABC, abstractmethod
from attack_predictor_libs.dataset.dataset import Dataset

class Metric(ABC):
    
    def __init__(self):
        self._value = None

    @property
    def value(self) -> any:
        return self._value
    
    @property
    def is_already_evaluated(self) -> bool:
        return self._value is not None
    
    @abstractmethod
    def evaluate(self, Dataset: Dataset, savedir: str | None = None) -> None:
        raise NotImplementedError
    
    
    