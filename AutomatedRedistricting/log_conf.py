import logging

def singleton(cls):
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()

@singleton
class Logger():
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='/home/reka/Documents/redistricting/AutomatedRedistricting/log/logs.log',
                    filemode='w',
                    level=logging.INFO)
        self.logr = logging.getLogger('root')
