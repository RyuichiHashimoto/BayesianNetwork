from enum import Enum
from abc import ABC, abstractmethod
from pgmpy.estimators import BicScore, AICScore, K2Score, BDeuScore
from pgmpy.estimators import StructureScore
from attack_predictor_libs.predictor.scorefunction.custom_score_function import CustomBicScore
from functools import lru_cache

        
class ScoreFunctionEnum(Enum):
    bic = BicScore
    aic = AICScore
    bdeu = K2Score
    k2 = BDeuScore
    custom_bic = CustomBicScore
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_score_function_class(cls, score_function: str) -> StructureScore:
        return cls[score_function].value
        

if __name__ == "__main__":
    print(ScoreFunctionEnum.get_score_function_class("custom_bic"))
    