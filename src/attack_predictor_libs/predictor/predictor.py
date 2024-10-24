from abc import abstractmethod
from attack_predictor_libs.dataset.dataset import Dataset
from attack_predictor_libs._exception import AttackLibException
from attack_predictor_libs.predictor.scorefunction.score_function import ScoreFunctionEnum
import polars as pl
class PredictorParameter:
    
    @classmethod
    def from_dict(cls, data):
        
        if isinstance(data, dict):
            return cls(**data)
        elif isinstance(data, cls):
            return data
        else:
            print(type(data))
            print(cls.__name__)
            raise TypeError(f"Expected dict or {type(cls)} instance")

class Predictor:
    def __init__(self, param: PredictorParameter):
        self._param = param
        self._network = None
        self._done_learn_structure = False
        self._done_learn_parameter = False
    
    @property
    def parameter(self) -> PredictorParameter:
        return self._param
    
    @property
    def network(self):
        if self._network is None:
            raise AttackLibException("Network is not learned")
        return self._network
    
    
    def learn_structure(self, dataset: pl.DataFrame):
        if self._done_learn_structure:
            raise AttackLibException("Network is already learned")
        
        self._learn_structure(dataset)
        self._done_learn_structure = True
    
    def learn_parameter(self, dataset: pl.DataFrame):
        if not self._done_learn_structure:
            raise AttackLibException("Network is not learned yet")
        
        if self._done_learn_parameter:
            raise AttackLibException("Parameter is already learned")
        
        self._learn_parameter(dataset)
        self._done_learn_parameter = True
        
    
    @abstractmethod
    def _learn_structure(self, dataset: pl.DataFrame):
        raise NotImplementedError
        
    @abstractmethod
    def _learn_parameter(self, dataset: pl.DataFrame):
        raise NotImplementedError
    
    
    @abstractmethod
    def predict(self, dataset: Dataset):
        raise NotImplementedError

if __name__ == "__main__":
    param = PredictorParameter()

    print(param.__dict__)