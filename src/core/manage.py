import click
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.api import api_router
from src.core import server
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from src.db_util.connection import CommunicationsSQLAlchemyConnectionManager
from src.core.server import create_app
from src.log_conf import Logger


LOGGER = Logger.get_logger(__name__)


@click.group("Fast-api App manager")
def manage() -> None:
    # the main group of commands
    pass


@manage.command(help="Run the web server")
def run_server() -> None:
    click.echo("-> Running the server")
    run()


@manage.group(help="Manage the database")
def database() -> None:
    # group to manage database
    pass


app: FastAPI = create_app()
app.include_router(api_router, prefix="/rag_chat_storage/api")

LOGGER.info("Initialize CORS configurations ...")

origins = server.settings().backend_cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup() -> None:
    pass
    # LOGGER.info("Running startup tasks... Creating tables if not exist.")
    # sql_obj = CommunicationsSQLAlchemyConnectionManager()
    # engine = sql_obj.get_engine()
    # Base.metadata.create_all(bind=engine)
    # LOGGER.info("All tables ensured.")


# @app.on_event("startup")
# async def startup():
#     await start_task()


def run() -> None:
    uvicorn.run(
        "src.core.manage:app",
        host=server.settings().server_address,
        port=server.settings().server_port,
        log_level=server.settings().server_log_level,
        workers=3
    )


if __name__ == "__main__":
    manage()
