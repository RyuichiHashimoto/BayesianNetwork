from attack_predictor_libs.dataset.dataset import Dataset
from .metric import Metric
import seaborn as sns
import matplotlib.pyplot as plt
import os

class CorrelationMatrixHeatmap(Metric):
    
    def evaluate(self, dataset: Dataset, outoutfolder: str | None = None) -> None:
        self._value = dataset.data.to_pandas().corr()
        
        if outoutfolder is not None:
            sns.heatmap(self._value,
                square=True,
                cmap='coolwarm',
                xticklabels=self._value.columns.values,
                yticklabels=self._value.columns.values,
            )
            savepath = os.path.join(outoutfolder, "correlation_matrix_heatmap.png")
            os.makedirs(os.path.dirname(savepath), exist_ok=True)
            plt.savefig(savepath)
            
        
    
    