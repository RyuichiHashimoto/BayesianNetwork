from common_libs.mlelogger import init_logging
from attack_predictor_libs.dataset.wine_dataset import WineDataset
from attack_predictor_libs.metric.correlation_matrix_heatmap import CorrelationMatrixHeatmap
from attack_predictor_libs.predictor.hill_climb_search_predictor import HillClimbSearchPredictor
from attack_predictor_libs.predictor.predictor import PredictorParameter
import logging
import networkx as nx
import matplotlib.pyplot as plt
logger = logging.getLogger(__name__)


def evaluate(model_parameter: PredictorParameter, outputdir: str):
    logger.info("load dataset")
    dataset = WineDataset("/home/work/dataset/wine/wine.csv")

    logger.info("training model")
    model = HillClimbSearchPredictor(model_parameter)
    model.fit(dataset)

    edge_list = list(model.network.edges())
    g = nx.DiGraph()
    logger.info("edge")
    logger.info(model.network.edges())
    for e in edge_list:
        src = e[0]
        dst = e[1]
        g.add_edge(src,dst,weight=0.5)
        logger.info(f"add edge {src} -> {dst}")
    # GraphML形式で保存
    nx.draw(g, with_labels=True)
    plt.savefig("sample.png")

    # nx.write_graphml(g, 'network_model.graphml')



    
    
    logger.info("evaluate result")
    metrix = CorrelationMatrixHeatmap()
    metrix.evaluate(dataset, outputdir)





    

if __name__ == "__main__":
    import os 
    from attack_predictor_libs.predictor.hill_climb_search_predictor import HillClimbSearchPredictorParameter

    logfolder = "result/sample"
    init_logging(os.path.join(logfolder, "log.log"))

    dic = {"score_funciton": "BIC"}
    


    evaluate(dic, "result/sample")