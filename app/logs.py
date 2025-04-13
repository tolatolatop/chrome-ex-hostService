import logging
from app.settings import LOG_LEVEL, LOG_FORMAT, LOG_HANDLERS


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=LOG_HANDLERS
    )


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的logger"""
    return logging.getLogger(name)
