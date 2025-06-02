import pytest
from sqlalchemy.orm.exc import NoResultFound
from fastapi import HTTPException, status
from unittest.mock import MagicMock
from src.utils.mysql_query_utils import get_field_details, get_all_field_details, create_field_details,\
    update_field_details


@pytest.mark.asyncio
async def test_get_field_details_success():
    query_model = 'Model'
    mock_db = MagicMock()
    mock_query_result = MagicMock()
    setattr(mock_query_result, "field_name", "field_value")
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_query_result
    result = await get_field_details(mock_db, query_model, {"query_field": "query_value"}, "field_name")
    assert result == "field_value"
    mock_db.query.assert_called_once_with(query_model)
    mock_db.query.return_value.filter_by.assert_called_once_with(query_field="query_value")
    mock_db.query.return_value.filter_by.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_get_field_details_empty_result():
    mock_db = MagicMock()
    query_model = 'Model'
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    result = await get_field_details(mock_db, query_model, {"query_field": "query_value"}, "field_name")
    assert result is None
    mock_db.query.assert_called_once_with(query_model)
    mock_db.query.return_value.filter_by.assert_called_once_with(query_field="query_value")
    mock_db.query.return_value.filter_by.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_get_field_details_exception():
    db = MagicMock()
    query_model = 'Model'
    db.query.return_value.filter_by.return_value = db.query.return_value  # Mock the chaining behavior
    db.query.return_value.with_entities.return_value.all.side_effect = Exception('Error')

    with pytest.raises(HTTPException) as exc_info:
        await get_field_details(db, query_model, {"query_field": "query_value"}, ["field_name"])
    assert exc_info.value.status_code == 500
    db.query.assert_called_once_with('Model')
    db.query.return_value.filter_by.return_value.first.side_effect = NoResultFound
    db.query.return_value.filter_by.assert_called_once_with(query_field="query_value")
    db.query.return_value.filter_by.return_value.first.assert_called_once()
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_get_all_field_details_success():
    db = MagicMock()
    query_result = [1, 2, 3]
    db.query.return_value.filter_by.return_value = db.query.return_value  # Mock the chaining behavior
    db.query.return_value.with_entities.return_value.all.return_value = query_result
    result = await get_all_field_details(db, 'Model', {'id': 1}, 'field1', 'field2')
    assert result == query_result

    db.query.assert_called_once_with('Model')
    db.query.return_value.filter_by.assert_called_once_with(id=1)
    db.query.return_value.with_entities.assert_called_once_with('field1', 'field2')
    db.query.return_value.with_entities.return_value.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_field_details_no_result_found_exception():
    db = MagicMock()
    db.query.return_value.filter_by.return_value = db.query.return_value
    db.query.return_value.with_entities.return_value.all.side_effect = NoResultFound

    result = await get_all_field_details(db, 'Model', {'id': 1}, 'field1', 'field2')
    assert result is None
    db.query.assert_called_once_with('Model')
    db.query.return_value.filter_by.assert_called_once_with(id=1)


@pytest.mark.asyncio
async def test_get_all_field_details_generic_exception():
    db = MagicMock()
    db.query.return_value.filter_by.return_value = db.query.return_value  # Mock the chaining behavior
    db.query.return_value.with_entities.return_value.all.side_effect = Exception('Error')

    with pytest.raises(HTTPException) as exc_info:
        await get_all_field_details(db, 'Model', {'id': 1}, 'field1', 'field2')
    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == 'Error'

    db.query.assert_called_once_with('Model')
    db.query.return_value.filter_by.assert_called_once_with(id=1)
    db.query.return_value.with_entities.assert_called_once_with('field1', 'field2')
    db.query.return_value.with_entities.return_value.all.assert_called_once()


@pytest.mark.asyncio
async def test_create_field_details_success():
    mock_db = MagicMock()
    mock_query_model = MagicMock()
    await create_field_details(mock_db, mock_query_model, {"field1": "value1", "field2": "value2"})
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_query_model.assert_called_once()
    mock_query_model_instance = mock_query_model.return_value
    mock_query_model_instance.field1 = "value1"
    mock_query_model_instance.field2 = "value2"


@pytest.mark.asyncio
async def test_create_field_details_exception():
    mock_db = MagicMock()
    mock_db.add.side_effect = Exception("test_error")
    mock_query_model = MagicMock()
    with pytest.raises(HTTPException) as exc_info:
        await create_field_details(mock_db, mock_query_model, {"field1": "value1"})
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert str(exc_info.value.detail) == "test_error"
    mock_db.add.assert_called_once()
    mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_field_details_success():
    mock_db = MagicMock()
    mock_query_model = MagicMock()
    mock_query_object = {"id": 1}
    mock_update_object = {"field1": "new_value"}
    mock_query_details = MagicMock()
    mock_query_details.field1 = "old_value"
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = mock_query_details
    mock_db.query.return_value = mock_query
    await update_field_details(mock_db, mock_query_model, mock_query_object, mock_update_object)
    mock_query_details.field1 = "new_value"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_query_details)


@pytest.mark.asyncio
async def test_update_field_details_exception():
    # Mock the database session, query model, query object, and update object to raise an exception
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("test_error")
    mock_query_model = MagicMock()
    mock_query_object = {"id": 1}
    mock_update_object = {"field1": "new_value"}
    with pytest.raises(HTTPException) as exc_info:
        await update_field_details(mock_db, mock_query_model, mock_query_object, mock_update_object)
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert str(exc_info.value.detail) == "test_error"
