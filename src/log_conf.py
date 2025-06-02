'''
log_conf.py
This python module will configure application level logging format by loading logging.conf file.
'''
import os
import logging.config


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance()


@singleton
class Logger:
    def __init__(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'logging.conf')
        logging.config.fileConfig(conf_file, disable_existing_loggers=False)

    def get_logger(self, __name__):
        return logging.getLogger(__name__)