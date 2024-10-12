from abc import abstractmethod
from attack_predictor_libs.dataset.dataset import Dataset
from attack_predictor_libs._exception import AttackLibException
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
    
    @property
    def parameter(self):
        return self._param
    
    @property
    def network(self):
        if self._network is None:
            raise AttackLibException("Network is not learned")
        return self._network
    
    @abstractmethod
    def predict(self, dataset: Dataset):
        raise NotImplementedError

    @abstractmethod
    def fit(self, dataset: Dataset):
        raise NotImplementedError



if __name__ == "__main__":
    param = PredictorParameter()

    print(param.__dict__)