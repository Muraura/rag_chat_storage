import pytest

from unittest import mock
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from src.core.manage import app
from src.services.workday import get_workday_entities,get_workday_entity
from src.db_util import models
from tests.test_fixtures import mock_response


client = TestClient(app)
db = Session()


def test_fetch_workday_entities_success():
    with patch("src.api.endpoints.workday_integration.get_workday_entities") as mock_get_workday_entities:
        mock_payload = {"company_id": 1, "entity": "test_entity"}
        mock_get_workday_entities.return_value = "event_message"
        response = client.post("/integration-service/api/v1/workday/fetch-workday-entities", json=mock_payload)
        assert response.status_code == 200
        assert response.json() == "event_message"


def test_fetch_workday_entities_error():
    with patch("src.api.endpoints.workday_integration.get_workday_entities") as mock_get_workday_entities:
        mock_payload = {"company_id": 1, "entity": "test_entity"}
        mock_get_workday_entities.side_effect = Exception("test_error")
        response = client.post("/integration-service/api/v1/workday/fetch-workday-entities", json=mock_payload)
        assert response.status_code == 500
        assert response.json() == {"detail": "test_error"}


@pytest.mark.asyncio
async def test_get_workday_entities_function_success():
    with patch("src.services.workday.field_validation") as mock_field_validation, \
            patch("src.services.workday.get_field_details") as mock_get_field_details, \
            patch("src.services.workday.get_workday_entity") as mock_get_workday_entity, \
            patch("src.services.workday.read_dataframe_data") as mock_read_dataframe_data, \
            patch("src.services.workday.get_dataframe_details") as mock_get_dataframe_details, \
            patch("src.services.workday.produce_message_to_kafka") as mock_produce_kafka_message:
        mock_db = MagicMock()
        mock_request = {"company_id": "123", "entity": "test_entity"}
        mock_field_validation.return_value = None
        mock_get_field_details.return_value = "test_company_name"
        mock_get_workday_entity.return_value = [{"id": 1, "name": "Test Entity"}]
        mock_read_dataframe_data.return_value = MagicMock()
        mock_get_dataframe_details.return_value = {"topic": "test_topic", "kafka_broker": "test_broker"}
        response = await get_workday_entities(mock_db, mock_request)
        assert response == {"status": "Successfully fetched workday events"}
        mock_field_validation.assert_called_once_with(mock_request, [
            {"field": "company_id", "alias": "Company Id"},
            {"field": "entity", "alias": "Entity"}
        ])
        mock_get_field_details.assert_called_once_with(mock_db, models.Company, {"id": "123"}, "company_name")
        mock_read_dataframe_data.assert_called_once()
        mock_get_dataframe_details.assert_called_once_with(mock_read_dataframe_data.return_value, "backup",
                                                           "test_entity")
        mock_produce_kafka_message.assert_called_once_with("test_broker", "test_topic", {
            "company_id": "123",
            "s3_file_name": mock.ANY,
            "entity": "test_entity",
            "source": "workday",
            "destination": "canvas",
            "entity_data_list": [{"id": 1, "name": "Test Entity"}]
        })


@pytest.mark.asyncio
async def test_get_workday_entities_function_failure():
    with patch("src.services.workday.field_validation") as mock_field_validation:
        mock_db = MagicMock()
        mock_request = {"company_id": "123", "entity": "test_entity"}
        mock_field_validation.return_value = "Invalid request data."
        response = await get_workday_entities(mock_db, mock_request)
        assert response.status_code == 400
        mock_field_validation.assert_called_once_with(mock_request, [
            {"field": "company_id", "alias": "Company Id"},
            {"field": "entity", "alias": "Entity"}
        ])
        response_json = response.body.decode("utf-8")
        expected_json = '{"detail":"Invalid request data."}'
        assert response_json == expected_json


@pytest.mark.asyncio
async def test_get_workday_entities_no_data():
    with patch("src.services.workday.field_validation") as mock_field_validation, \
            patch("src.services.workday.get_field_details") as mock_get_field_details, \
            patch("src.services.workday.get_workday_entity") as mock_get_workday_entity, \
            patch("src.services.workday.read_dataframe_data") as mock_read_dataframe_data, \
            patch("src.services.workday.get_dataframe_details") as mock_get_dataframe_details, \
            patch("src.services.workday.produce_message_to_kafka") as mock_produce_kafka_message:
        mock_db = MagicMock()
        mock_request = {"company_id": "123", "entity": "test_entity"}
        mock_field_validation.return_value = None
        mock_get_workday_entity.return_value = []
        response = await get_workday_entities(mock_db, mock_request)
        response_json = response
        expected_json = {"status": "No new workday entities to be fetched"}
        assert response_json == expected_json


@pytest.mark.asyncio
async def test_get_workday_entity_success(mock_response):
    with patch("src.services.workday.BMS_JOB_PULL_CONFIG") as mock_bms_job_pull_config, \
            patch("src.services.workday.SOAPService") as mock_soap_service:
        mock_path = "BMS"
        mock_entity = "job"
        mock_soap_service.return_value.get_data.return_value = mock_response
        result = await get_workday_entity(mock_path, mock_entity)
        mock_bms_job_pull_config.assert_called_once_with(page_number=1, from_date=mock.ANY, to_date=mock.ANY)
        mock_soap_service.assert_called_once_with(url=mock.ANY, payload=mock.ANY)
        mock_soap_service.return_value.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_get_workday_entity_exception():
    with patch("src.services.workday.BMS_JOB_PULL_CONFIG") as mock_bms_job_pull_config, \
            patch("src.services.workday.SOAPService") as mock_soap_service:
        mock_path = "BMS"
        mock_entity = "job"
        mock_soap_service.return_value.get_data.side_effect = Exception("SOAP Service error")

        try:
            result = await get_workday_entity(mock_path, mock_entity)
            assert False
        except Exception as e:
            assert str(e) == "SOAP Service error"
        mock_bms_job_pull_config.assert_called_once_with(page_number=1, from_date=mock.ANY, to_date=mock.ANY)
        mock_soap_service.assert_called_once_with(url=mock.ANY, payload=mock.ANY)
        mock_soap_service.return_value.get_data.assert_called_once()
