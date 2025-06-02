from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

import logging

logger = logging

from enum import Enum


class SenderEnum(str, Enum):
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"


async def get_field_details(db: Session, query_model, query_object, get_field):
    try:
        query_result = db.query(query_model).filter_by(**query_object).first()
        logger.info(
            f"#mysql_query_utils.py #get_field_details #successfully fetched field details, "
            f"query_result,{query_result}")
        if query_result:
            return getattr(query_result, get_field)
        else:
            return None
    except NoResultFound:
        logger.info(
            f"#mysql_query_utils.py #get_field_details #query did not return any result query_model, {query_model} ,"
            f"query_object,{query_object}, ")
        return None
    except Exception as e:
        logger.error(
            f"#mysql_query_utils.py  #get_field_details #exception_getting_query_object_details #Exception, {e}",
            exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_all_field_details(db: Session, query_model, query_object, *get_fields):
    try:
        query_result = db.query(query_model).filter_by(**query_object)
        if get_fields:
            query_result = query_result.with_entities(*get_fields)
            query_result = query_result.all()
        logger.info(
            f"#mysql_query_utils.py #get_all_field_details #successfully fetched all field details")
        return query_result
    except NoResultFound:
        logger.info(
            f"#mysql_query_utils.py #get_all_field_details #query did not return any result query_model, {query_model},"
            f"query_object,{query_object}, ")
        return None
    except Exception as e:
        logger.error(
            f"#mysql_query_utils.py  #get_field_details #exception_getting_query_object_details #Exception, {e}",
            exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def create_field_details(db: Session, query_model, query_object):
    try:
        model_instance = query_model()
        for field, value in query_object.items():
            setattr(model_instance, field, value)
        db.add(model_instance)
        db.commit()
        logger.info(
            f"#mysql_query_utils.py #create_field_details #successfully created query_object, query_model,{query_model}"
            f",query_object,{query_object}")
    except Exception as e:
        db.rollback()
        logger.error(
            f"#mysql_query_utils.py  #create_field_details #exception_creating_query_object #Exception, {e}",
            exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update_field_details(db: Session, query_model, query_object, update_object):
    try:
        query_details = db.query(query_model).filter_by(**query_object).first()
        if not query_details:
            logger.warning(
                f"#mysql_query_utils.py #update_field_details #Not found for {query_model} with {query_object}")
            return False

        for field, value in update_object.items():
            setattr(query_details, field, value)

        db.commit()
        db.refresh(query_details)

        logger.info(
            f"#mysql_query_utils.py #update_field_details #Updated {query_model.__name__} with {update_object}")
        return True

    except Exception as e:
        logger.error(
            f"#mysql_query_utils.py #update_field_details #Exception: {e}",
            exc_info=True
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database update failed")




async def get_last_run_from_run_history(db: Session, query_model, query_object, max_value_field):
    try:
        query_result = db.query(query_model).filter_by(**query_object).order_by(getattr(query_model, max_value_field).desc()).first()
        logger.info(
            f"#mysql_query_utils.py #get_field_with_max_value #successfully fetched field details, "
            f"query_result,{query_result}")
        if query_result:
            return query_result.__dict__
        else:
            return None
    except NoResultFound:
        logger.info(
            f"#mysql_query_utils.py #get_field_with_max_value #query did not return any result query_model, {query_model} ,"
            f"query_object,{query_object}, ")
        return None
    except Exception as e:
        logger.error(
            f"#mysql_query_utils.py  #get_field_with_max_value #exception_getting_query_object_details #Exception, {e}",
            exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_field_details(db: Session, model, filters: dict):
    try:
        record = db.query(model).filter_by(**filters).first()
        if not record:
            logger.warning(f"#mysql_query_utils.py #delete_field_details #No record found for filters: {filters}")
            raise HTTPException(status_code=404, detail="Record not found")

        db.delete(record)
        db.commit()

        logger.info(
            f"#mysql_query_utils.py #delete_field_details #Deleted record from {model.__name__} with filters {filters}")
        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"#mysql_query_utils.py #delete_field_details #Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete record")
