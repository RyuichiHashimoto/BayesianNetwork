from abc import ABCMeta, abstractmethod

class PredictorParameter:
    @classmethod
    def from_dict(cls, data):
        
        if isinstance(data, dict):
            return cls(**data)
        elif isinstance(data, cls):
            return data
        else:
            raise TypeError(f"Expected dict or {cls.__class__.__name__} instance")

class Predictor:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @abstractmethod
    def predict(self, dataset: Dataset):
        raise NotImplementedError

    @abstractmethod
    def learn(self, dataset: Dataset):
        raise NotImplementedError



if __name__ == "__main__":
    param = PredictorParameter()

    print(param.__dict__)