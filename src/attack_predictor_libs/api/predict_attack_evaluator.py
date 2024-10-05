from common_libs.mlelogger import init_logging
from attack_predictor_libs.dataset.wine_dataset import WineDataset
from attack_predictor_libs.metric.correlation_matrix_heatmap import CorrelationMatrixHeatmap
import logging

logger = logging.getLogger(__name__)


def evaluate(outputdir: str):
    logger.info("load dataset")
    dataset = WineDataset("/home/work/dataset/wine/wine.csv")
    
    metrix = CorrelationMatrixHeatmap()

    logger.info("evaluate result")
    metrix.evaluate(dataset, outputdir)





    

if __name__ == "__main__":
    import os 
    logfolder = "result/sample"
    init_logging(os.path.join(logfolder, "log.log"))
    


    evaluate("result/sample")