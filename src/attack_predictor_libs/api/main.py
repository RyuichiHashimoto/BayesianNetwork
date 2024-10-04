from common_libs.mlelogger import init_logging
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    init_logging("log.txt")
    
    logger.info("hogehoge")