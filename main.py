import os

from config.config import Config
from config.logger_manager import LoggerManager
from app.app import Application

def main():
    config = Config.from_file(os.path.abspath("config/config.yaml"))
    config.merge(config)
    logger = LoggerManager.get_logger(config.log)

    app = Application(config.app, logger)
    app.run()

if __name__ == "__main__":
    main()

