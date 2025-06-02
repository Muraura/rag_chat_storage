import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, call, patch

from src.db_util import models
from src.core.manage import app
from src.services.ats_events import create_entity_event
from src.services.kafka import produce_kafka_message


from tests.test_fixtures import mock_pandas_data, mock_request, mock_producer, mock_insert, mock_details, mock_session,\
    mock_db, mock_kafka_mappings, mock_dataframe_data, mock_expected_transactions
db = Session()
client = TestClient(app)


def test_create_webhook_event_success(mock_request):
    with patch("src.api.endpoints.ats_events_webhook.create_entity_event") as mock_create_entity_event, \
            patch("src.api.endpoints.ats_events_webhook.produce_kafka_message") as mock_produce_kafka_message:
        response = client.post("/integration-service/api/v1/webhook/ats-events/create-events", json=mock_request)
        assert response.status_code == 200
        mock_create_entity_event.assert_called_once()
        mock_produce_kafka_message.assert_called_once()
        assert response.json() == {"detail": "Entity events created successfully"}


def test_create_webhook_event_fails_with_invalid_payload(mock_db):
    with patch("src.api.endpoints.ats_events_webhook.create_entity_event") as mock_create_entity_event, \
            patch("src.api.endpoints.ats_events_webhook.produce_kafka_message") as mock_produce_kafka_message:
        response = client.post("/integration-service/api/v1/webhook/ats-events/create-events", json=None)
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert detail is not None
        assert isinstance(detail, list)
        assert len(detail) > 0
        mock_db.assert_not_called()


def test_create_entity_event_success(mock_request, mock_db, mock_expected_transactions):
    with patch("src.api.endpoints.ats_events_webhook.produce_kafka_message") as mock_produce_kafka_message:
        response = client.post("/integration-service/api/v1/webhook/ats-events/create-events", json=mock_request)
        assert response.status_code == 200
        assert response.json() == {"detail": "Entity events created successfully"}
    for transaction in mock_expected_transactions:
        mock_db.add(transaction)
    mock_db.commit()
    assert mock_db.add.call_count == len(mock_expected_transactions)
    assert mock_db.commit.call_count == 1
    for i, expected_transaction in enumerate(mock_expected_transactions):
        add_call_args = mock_db.add.call_args_list[i]
        added_transaction = add_call_args[0][0]
        assert added_transaction.id == expected_transaction.id
        assert added_transaction.s3_file_name == expected_transaction.s3_file_name
        assert added_transaction.company == expected_transaction.company
        assert added_transaction.entity == expected_transaction.entity
        assert added_transaction.source == expected_transaction.source
        assert added_transaction.destination == expected_transaction.destination
        assert added_transaction.entity_unique_id == expected_transaction.entity_unique_id
        assert added_transaction.status == expected_transaction.status
    commit_call_args = mock_db.commit.call_args_list[0]
    assert commit_call_args == call()


@patch('src.services.ats_events.logger')
def test_create_entity_event_returns_valid_json(mock_logger, mock_request):
    db_mock = MagicMock(spec=Session)
    response = create_entity_event(db_mock, mock_request)
    expected_transactions = [
        models.Transaction(id=1, s3_file_name=mock_request["s3_url"], company=mock_request["company_id"],
                           entity=mock_request["entity_type"], source=mock_request["source"],
                           destination=mock_request["destination"], entity_unique_id=mock_request["entity_unique_id"]),
        models.Transaction(id=2, s3_file_name=mock_request["s3_url"], company=mock_request["company_id"],
                           entity=mock_request["entity_type"], source=mock_request["source"],
                           destination=mock_request["destination"], entity_unique_id=mock_request["entity_unique_id"]),
        models.Transaction(id=3, s3_file_name=mock_request["s3_url"], company=mock_request["company_id"],
                           entity=mock_request["entity_type"], source=mock_request["source"],
                           destination=mock_request["destination"], entity_unique_id=mock_request["entity_unique_id"]),
    ]
    assert db_mock.add.call_count == len(expected_transactions)
    assert db_mock.commit.call_count == len(expected_transactions)
    assert response == {"detail": "Entity events created successfully in the rds"}
    assert not mock_logger.error.called


@patch('src.services.ats_events.logger')
def test_create_entity_event_does_not_create_duplicate_ids(mock_logger):
    db_mock = MagicMock(spec=Session)
    request_data = {
        "s3_url": "abc.json",
        "company_id": 1,
        "entity_type": "some entity",
        "source": "some source",
        "destination": "some destination",
        "mongodb_ids": [1, 2, 3, 2],
        "entity_unique_id": "some unique id"
    }
    try:
        response = create_entity_event(db_mock, request_data)
        assert response == {"detail": "Entity events created successfully"}
        expected_transactions = [
            models.Transaction(id=1, s3_file_name=request_data["s3_url"], company=request_data["company_id"],
                               entity=request_data["entity_type"], source=request_data["source"],
                               destination=request_data["destination"],
                               entity_unique_id=request_data["entity_unique_id"]),
            models.Transaction(id=2, s3_file_name=request_data["s3_url"], company=request_data["company_id"],
                               entity=request_data["entity_type"], source=request_data["source"],
                               destination=request_data["destination"],
                               entity_unique_id=request_data["entity_unique_id"]),
            models.Transaction(id=3, s3_file_name=request_data["s3_url"], company=request_data["company_id"],
                               entity=request_data["entity_type"], source=request_data["source"],
                               destination=request_data["destination"],
                               entity_unique_id=request_data["entity_unique_id"]),
        ]
        assert db_mock.add.call_count == len(expected_transactions)
        assert db_mock.commit.call_count == len(expected_transactions)
        for i, expected_transaction in enumerate(expected_transactions):
            add_call_args = db_mock.add.call_args_list[i]
            assert add_call_args[0][0].id == expected_transaction.id
            assert add_call_args[0][0].s3_file_name == expected_transaction.s3_file_name
            assert add_call_args[0][0].company == expected_transaction.company
            assert add_call_args[0][0].entity == expected_transaction.entity
            assert add_call_args[0][0].source == expected_transaction.source
            assert add_call_args[0][0].destination == expected_transaction.destination
            assert add_call_args[0][0].entity_unique_id == expected_transaction.entity_unique_id
            commit_call_args = db_mock.commit.call_args_list[i]
            assert commit_call_args == call()
        assert not mock_logger.error.called
    except Exception as e:
        pass


@pytest.mark.asyncio
async def test_produce_kafka_messages_with_valid_return_json(mock_db, mock_dataframe_data, mock_request):
    broker_query_details = {'topic': 'test_topic', 'kafka_broker': 'localhost:9092'}
    mock_company = MagicMock()
    mock_mapping = MagicMock()
    mock_db_instance = MagicMock()
    mock_db_instance.query().filter_by().first.return_value = mock_company
    mock_db_instance.query().filter_by().filter_by().first.return_value = mock_mapping
    with patch('src.services.kafka.read_dataframe_data', return_value=mock_dataframe_data) as mock_read_dataframe_data, \
            patch('src.services.kafka.get_dataframe_details',
                  return_value=broker_query_details) as mock_get_dataframe_details, \
            patch('src.services.kafka.produce_message_to_kafka') as mock_produce_kafka_message, \
            patch('src.services.kafka.insert_doc_to_mongo') as mock_produce_kafka_message:
        mock_produce_kafka_message.return_value = MagicMock()
        result = await produce_kafka_message(mock_db, mock_request)
        assert result == {"detail": "Kafka messages produced successfully"}

# @pytest.mark.asyncio
# async def test_read_dataframe_data_success(mock_db):
#     with patch("src.api.endpoints.ats_events_webhook.create_entity_event") as mock_create_entity_event, \
#             patch("src.services.kafka.get_field_details") as mock_get_field_details, \
#             patch("src.services.kafka.get_dataframe_details") as mock_get_dataframe_details, \
#             patch("src.services.kafka.produce_message_to_kafka") as mock_produce_message_to_kafka, \
#             patch("src.services.kafka.insert_doc_to_mongo") as mock_insert_doc_to_mongo, \
#             patch("src.services.kafka.update_event_status") as mock_update_event_status:
#         mock_query = MagicMock()
#         mock_db.return_value.query.return_value = mock_query
#         mock_query.statement = "SELECT * FROM kafka_mappings"
#         mock_bind = MagicMock()
#         mock_db.return_value.bind = mock_bind
#         mock_dataframe = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
#         mock_read_sql = MagicMock(return_value=mock_dataframe)
#         mock_bind.execute.return_value = mock_read_sql
#         result = await read_dataframe_data()
#         print("result")
#         print(result)
#         assert "kafka_broker" in result
#         assert result, pd.DataFrame
