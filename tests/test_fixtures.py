import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, Mock
import pandas as pd

from src.core.manage import app
from src.db_util import models

db = Session()
client = TestClient(app)


@pytest.fixture
def mock_producer():
    return MagicMock()


@pytest.fixture
def mock_insert():
    return MagicMock()


@pytest.fixture
def mock_details():
    return MagicMock()


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture()
def mock_db():
    return Mock(spec=Session)


@pytest.fixture()
def mock_kafka_mappings():
    return {
        "client_group": ["group1", "group2"],
        "entity": ["entity1", "entity2"],
        "topic": ["topic1", "topic2"],
        "kafka_broker": ["broker1", "broker2"]
    }


@pytest.fixture()
def mock_dataframe_data():
    kafka_mappings = {
                'kafka_mappings': {

                    'id': {
                        0: 1
                    },
                    'client_group': {
                        0: 'A'
                    },
                    'entity': {
                        0: 'apps'
                    },
                    'topic': {
                        0: 'A-apps'
                    },
                    'partitions': {
                        0: 1
                    },
                    'retry_topic': {
                        0: 1
                    },
                    'no_of_retries': {
                        0: 1
                    },
                    'dl_topic': {
                        0: 'A-apps-dl'
                    },
                    'consumer_group': {
                        0: 'A-apps-1'
                    },
                    'kafka_broker': {
                        0: '192.168.100.40:9092'
                    },
                    'compression_type': {
                        0: None
                    },
                    'batch_size': {
                        0: None
                    }
                    }
                }

    df = pd.DataFrame(kafka_mappings['kafka_mappings'])
    df_data = {"kafka_mappings": df}
    return df_data


@pytest.fixture()
def mock_pandas_data():
    kafka_mappings_dataframe = pd.DataFrame({
        "client_group": ["group1", "group2"],
        "entity": ["entity1", "entity2"],
        "topic": ["topic1", "topic2"],
        "kafka_broker": ["broker1", "broker2"]
    })
    return kafka_mappings_dataframe


@pytest.fixture
def mock_request():
    return {
        "company_id": 1,
        "source": "test_source",
        "destination": "test_destination",
        "entity_type": "test_entity",
        "s3_url": "uuid_timestamp.json",
        "entity_mongodb_ids": ["id1", "id2", "id3"],
        "entity_unique_id": "e556"
    }


@pytest.fixture
def mock_expected_transactions():
    return [
        models.Transaction(
            id=1,
            s3_file_name="example_file_1",
            company="example_company_1",
            entity="example_entity_1",
            source="example_source_1",
            destination="example_destination_1",
            entity_unique_id="example_unique_id_1"
        ),
        models.Transaction(
            id=2,
            s3_file_name="example_file_2",
            company="example_company_2",
            entity="example_entity_2",
            source="example_source_2",
            destination="example_destination_2",
            entity_unique_id="example_unique_id_2"
        ),
        models.Transaction(
            id=3,
            s3_file_name="example_file_3",
            company="example_company_3",
            entity="example_entity_3",
            source="example_source_3",
            destination="example_destination_3",
            entity_unique_id="example_unique_id_3"
        ),
    ]


@pytest.fixture
def mock_response():
    return {
                "job_entities": [
                    {
                        "id": "1",
                        "title": "Job 1"
                    },
                    {
                        "id": "2",
                        "title": "Job 2"
                    }
                ],
                "total_pages": "1"
            }
