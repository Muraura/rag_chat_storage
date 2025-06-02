import pytest

from fastapi import HTTPException, status, FastAPI
from pandas import DataFrame
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

from src.db_util import models
from src.core.manage import app
from src.utils.dataframe_utils import get_dataframe_details, create_dataframe_data, read_dataframe_data

from tests.test_fixtures import mock_pandas_data, mock_request, mock_producer, mock_insert, mock_details, mock_session, \
    mock_db, mock_kafka_mappings, mock_dataframe_data
db = Session()
client = TestClient(app)


@pytest.mark.asyncio
async def test_get_dataframe_details_success():
    mock_kafka_mappings_dataframe = MagicMock(spec=DataFrame)
    mock_group_name = "test_group"
    mock_entity = "test_entity"
    mock_filtered_dataframe = MagicMock(spec=DataFrame)
    mock_filtered_dataframe.iloc[0]['topic'] = "test_topic"
    mock_filtered_dataframe.iloc[0]['kafka_broker'] = "test_broker"
    mock_kafka_mappings_dataframe.__getitem__.return_value.__getitem__.side_effect = [
        mock_filtered_dataframe,
        mock_filtered_dataframe.iloc[0]['topic'],
        mock_filtered_dataframe.iloc[0]['kafka_broker']
    ]
    result = await get_dataframe_details(mock_kafka_mappings_dataframe, mock_group_name, mock_entity)
    assert result == {
        "topic": "test_topic",
        "kafka_broker": "test_broker"
    }


@pytest.mark.asyncio
async def test_get_dataframe_details_exception(mock_pandas_data):
    mock_group_name = ""
    mock_entity = "test_entity"
    with pytest.raises(HTTPException) as e:
        await get_dataframe_details(mock_pandas_data, mock_group_name, mock_entity)
    assert e.value.status_code == 500
    assert e.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_dataframe_details_missing_entity(mock_pandas_data):
    with pytest.raises(HTTPException) as e:
        await get_dataframe_details(mock_pandas_data, "group1", "")
    assert e.value.status_code == 500
    assert e.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_dataframe_data_exception():
    # Mock the database session to raise an exception
    mock_db = MagicMock()
    with pytest.raises(HTTPException) as exc_info:
        await create_dataframe_data(mock_db)
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
@pytest.mark.asyncio
async def test_read_dataframe_data_success():
    # Mock the DataFrame
    mock_dataframe = MagicMock()
    app.state.kafka_mappings_df = mock_dataframe

    # Patch the app state
    with patch.object(app, "state", app.state):
        # Call the function
        result = await read_dataframe_data()

        # Assert that the result is the mocked DataFrame
        assert result is mock_dataframe
