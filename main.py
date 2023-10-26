import os

from config.config import Config
from config.logger_manager import LoggerManager
from app.app import Application
from app_ipc.server import Server


def main():
    config = Config.from_file(os.path.abspath("config/config.yaml"))
    config.merge(config)
    logger = LoggerManager.get_logger(config.log)

    app = Application(config.app, logger)
    server = Server(app)

    app.launch()
    server.run()

if __name__ == "__main__":
    main()

