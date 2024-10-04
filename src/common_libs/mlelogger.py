# メインスクリプトでの複数ハンドラ設定
import logging


LOGFORMAT = '[%(asctime)s] [%(levelname)s] [pid=%(process)d] [module=%(filename)s] [line=%(lineno)d]: %(message)s'
DATEFORMAT =  '%Y/%m/%d %I:%M:%S'
# LOGFORMAT = '[%(asctime)s] [%(levelname)s] [pid=%(process)d] [module=%(filename)s] :  - %(levelname)s - %(message)s'

def init_logging(log_file: str = "") -> None:
    logger = logging.getLogger()
    

    for handler in logger.handlers[:]:  # ハンドラのコピーを取得
        logger.removeHandler(handler)
        handler.close()  # 必要に応じてハンドラを閉じる

    
    logger.setLevel(logging.DEBUG)

    # コンソールハンドラ
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(LOGFORMAT))
    logger.addHandler(ch)

    # ファイルハンドラ
    if log_file != "":
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(LOGFORMAT))
        logger.addHandler(fh)

    logging.captureWarnings(True) # Warningをロギングする