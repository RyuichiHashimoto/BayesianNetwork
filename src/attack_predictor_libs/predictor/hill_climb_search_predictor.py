import polars as pl
from attack_predictor_libs.dataset.dataset import Dataset
from attack_predictor_libs.predictor.predictor import Predictor, PredictorParameter
from pgmpy.estimators import HillClimbSearch
from attack_predictor_libs.predictor.scorefunction.score_function import ScoreFunctionEnum
from dataclasses import dataclass
from attack_predictor_libs._exception import AttackLibException
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.models import BayesianNetwork


@dataclass(frozen=True)
class HillClimbSearchPredictorParameter(PredictorParameter):
    score_function: str

class HillClimbSearchPredictor(Predictor):
    def __init__(self, param: dict | HillClimbSearchPredictorParameter):
        super().__init__(HillClimbSearchPredictorParameter.from_dict(param))
        
        
    def _learn_structure(self, dataset: pl.DataFrame):
        if self._network is not None:
            raise AttackLibException("Network is already learned")

        self._score_function = ScoreFunctionEnum(self._param.score_funciton)(dataset)
        self._search_algorithm = HillClimbSearch(dataset)
        self._network = self._search_algorithm.estimate(scoring_method=self._score_function)                
    
    def _learn_parameter(self, dataset: Dataset):
        estimator = MaximumLikelihoodEstimator(self._network, dataset.data_as_pandas).estimate()
        self._network = 
        
        
        self._network = PC(dataset.data_as_pandas)
        self._network = self._network.estimate()
        # self._network = HillClimbSearch(dataset.data_as_pandas)
        # self._network = self.network.estimate(scoring_method=self.score_function.get_score_function()(dataset.data_as_pandas))
        



class Predictor:
    def __init__(self, param: PredictorParameter):
        self._param = param
        self._network = None
    
    @property
    def parameter(self) -> PredictorParameter:
        return self._param
    
    @property
    def network(self):
        if self._network is None:
            raise AttackLibException("Network is not learned")
        return self._network
    
    @abstractmethod
    def learn_structure(self, dataset: pl.DataFrame):
        raise NotImplementedError
    
    @abstractmethod
    def learn_parameter(self, dataset: pl.DataFrame):
        raise NotImplementedError
    
    @abstractmethod
    def predict(self, dataset: Dataset):
        raise NotImplementedError



if __name__ == "__main__":
    param = HillClimbSearchPredictorParameter()

    print(param.__dict__)