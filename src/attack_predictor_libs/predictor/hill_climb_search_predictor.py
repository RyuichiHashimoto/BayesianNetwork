from attack_predictor_libs.dataset.dataset import Dataset
from attack_predictor_libs.predictor.predictor import Predictor, PredictorParameter
from dataclasses import dataclass
from enum import Enum
from pgmpy.estimators import HillClimbSearch, BicScore, K2Score, PC

class ScoreFunctionEnum(Enum):
    BIC = "bic"
    AIC = "aic"
    BDEU = "bdeu"
    K2 = "k2"
    
    
    def get_score_function(self):
        if self.value == "bic":
            return BicScore
        else:
            raise NotImplementedError(f"Score function {self.value} is not implemented")
        

@dataclass(frozen=True)
class HillClimbSearchPredictorParameter(PredictorParameter):
    score_funciton: str

class HillClimbSearchPredictor(Predictor):
    def __init__(self, param: dict | HillClimbSearchPredictorParameter):
        super().__init__(HillClimbSearchPredictorParameter.from_dict(param))
        self.score_function = ScoreFunctionEnum[self._param.score_funciton]

    def predict(self, dataset: Dataset):        
        raise NotImplementedError

    def fit(self, dataset: Dataset):
        self._network = PC(dataset.data_as_pandas)
        self._network = self._network.estimate()
        # self._network = HillClimbSearch(dataset.data_as_pandas)
        # self._network = self.network.estimate(scoring_method=self.score_function.get_score_function()(dataset.data_as_pandas))
        


if __name__ == "__main__":
    param = HillClimbSearchPredictorParameter()

    print(param.__dict__)