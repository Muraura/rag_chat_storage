import os
from fastapi import FastAPI
from src.config.app_config import FactoryConfig, load_s3_config
from src.log_conf import Logger

LOGGER = Logger.get_logger(__name__)
settings: FactoryConfig

setting_config = {}
environment = os.environ.get('ENVIRONMENT')
factory_config = FactoryConfig(environment)
setting_config.update(factory_config().config_data)

# # Load .env values
# load_dotenv()Ω
# Add ACCESS_TOKEN from .env
setting_config["ACCESS_TOKEN"] = os.environ.get("ACCESS_TOKEN")



def create_app() -> FastAPI:
    try:
        LOGGER.info("Initialize integration-microservice app")
        fast_app = FastAPI()

        LOGGER.info("Initialize application configurations ...")

        environment = os.environ.get('ENVIRONMENT')
        factory_config = FactoryConfig(environment)
        global settings
        settings = factory_config
        LOGGER.info("Config variables integration-microservice app : {}".format(str(settings)))
        LOGGER.info("Config variables integration-microservice app {} data:".format(type(settings)))

        return fast_app
    except Exception as e:
        LOGGER.error(f"Error in integration-microservice app initialisation => {e}")


def update_config_from_s3():
    global setting_config
    setting_config.update(load_s3_config())
    return setting_config
