from enum import Enum, auto
import polars as pl
from logging import getLogger


logger = getLogger(__name__)

PREPARATION_PHASE_LIST = ["Reconnaissance", "Resource Development", "Initial Access"]
INTRUSION_PHASE_LIST = ['Defense Evasion', 'Discovery', 'Collection', 'Lateral Movement', 'Execution', 'Credential Access', 'Command and Control', 'Privilege Escalation', 'Persistence']
COMPROMISE_PHASE_LIST = ['Impact', 'Exfiltration']
EXCEL_PATH = "/home/work/dataset/mitre/technique.xlsx"

EXCEL_DF = None
PREPARATION_DICT = {}
INTRUSION_DICT = {}
COMPROMISE_DICT = {}


def prepare_excel_df() -> None:
    """ Prepare excel dataframe """
    logger.info("Prepare excel dataframe")

    global EXCEL_DF, PREPARATION_DICT, INTRUSION_DICT, COMPROMISE_DICT
    if EXCEL_DF is not None:
        return
    
    EXCEL_DF = pl.read_excel(EXCEL_PATH)
    EXCEL_DF = EXCEL_DF.with_columns(pl.col("tactics").map_elements(lambda x: any(p in x for p in PREPARATION_PHASE_LIST ), return_dtype=bool).alias('contains_preparation'))
    EXCEL_DF = EXCEL_DF.with_columns(pl.col("tactics").map_elements(lambda x: any(p in x for p in INTRUSION_PHASE_LIST), return_dtype=bool).alias('contains_intrusion'))
    EXCEL_DF = EXCEL_DF.with_columns(pl.col("tactics").map_elements(lambda x: any(p in x for p in COMPROMISE_PHASE_LIST), return_dtype=bool).alias('contains_compromise'))
    
    PREPARATION_DICT = dict(zip(EXCEL_DF.get_column('ID').to_list(), EXCEL_DF.get_column('contains_preparation').to_list()))
    INTRUSION_DICT = dict(zip(EXCEL_DF.get_column('ID').to_list(), EXCEL_DF.get_column('contains_intrusion').to_list()))
    COMPROMISE_DICT = dict(zip(EXCEL_DF.get_column('ID').to_list(), EXCEL_DF.get_column('contains_compromise').to_list()))

    
    return 


prepare_excel_df()
    