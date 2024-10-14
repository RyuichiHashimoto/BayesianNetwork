from functools import lru_cache
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


class ExcelDFNotInitializedError(Exception):
    def __init__(self):
        super().__init__("EXCEL_DF is not initialized.")

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


def check_excel_df_initialized(func):
    """
    直接EXCEL_DFを触る関数にデコレータとして追加する。
    """
    def wrapper(*args, **kwargs):
        if EXCEL_DF is None:
            raise ExcelDFNotInitializedError()
        return func(*args, **kwargs)
    return wrapper


@check_excel_df_initialized
def get_technique_description_list(technique_id_list: list[str]) -> list[str]:
    """ Get technique description list """
    logger.info("Get technique description list")
    return EXCEL_DF.filter(pl.col("ID").isin(technique_id_list)).get_column("tactics").to_list()

@check_excel_df_initialized
@lru_cache(maxsize=128)
def _get_technique_record(technique_id: str) -> pl.DataFrame:
    """ Get technique record """
    ret = EXCEL_DF.filter(pl.col("ID") == technique_id)
    if len(ret) == 0:
        raise KeyError(f"Technique ID {technique_id} is not found.")
    return ret


def get_technique_description(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("description").to_list()[0]
    
def get_technique_name(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("name").to_list()[0]

def get_technique_url(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("url").to_list()[0]

def get_technique_tactic(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("tactics").to_list()[0]

		
def is_preparation_technique(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("contains_preparation").to_list()[0]

def is_intrusion_technique(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("contains_intrusion").to_list()[0]


def is_compromise_technique(technique_id: str) -> str:
    return _get_technique_record(technique_id).get_column("contains_compromise").to_list()[0]

def get_parent_technique(technique_id: str) -> str:
    """当該Techniqueの親Techniqueを取得する。もし親Techniqueがない場合はそのTechniqueIDを返す。"""
    return technique_id.split(".")[0]

def get_technique_phase(technique_id: str) -> str:
    try:
        one = PREPARATION_DICT[technique_id]
        two = INTRUSION_DICT[technique_id]
        three = COMPROMISE_DICT[technique_id]
    except:
        raise KeyError(f"Technique ID {technique_id} is not found.")
    
    if three:
        return "Compromise"        
    elif two:
        return "Intrusion"
    elif one:
        return "Preparation"
    else:
        raise Exception("Unexpected Error")
    
    if one:
        return "Preparation"
    elif two:
        return "Intrusion"
    elif three:
        return "Compromise"
    else:
        raise Exception("Unexpected Error")
    
    



prepare_excel_df()
    
