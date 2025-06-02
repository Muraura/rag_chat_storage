from src.db_util import models
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from fastapi.responses import  JSONResponse

from src.utils.mysql_query_utils import get_field_details,get_all_field_details, create_field_details,update_field_details
from src.utils.validation_util import field_validation, dict_field_validation
from src.utils.utils import sort_dict
from src.config.ats_config import ATS_FIELDS

import logging

logger = logging

async def get_field_mappings(db: Session, request: dict):
    validation_list = [{
        "field": "destination",
        "alias": "Destination"
    }, {
        "field": "entity",
        "alias": "Entity"
    }, {
        "field": "source",
        "alias": "Source"
    },
    ]
    messages = field_validation(request, validation_list)
    if messages:
        return JSONResponse(content={"detail": messages}, status_code=400)
    destination = request.get("destination", None)
    entity = request.get("entity", None)
    source = request.get("source", None)

    try:
        # get mapping_json from mapping rds table
        mapping_query_object = {
            "source": source,
            "destination": destination,
            "entity": entity
        }
        logger.info(
            f"#ui_apis.py  #get_field_mappings #create_dataframe_data #query_mapping_json_details,source:{source},"
            f" destination:{destination}, entity:{entity}")
        mapping_json = await get_field_details(db, models.Mapping, mapping_query_object, "mapping")

        if mapping_json is None:
            logger.info(
                f"#ui_apis.py  #get_field_mappings #get_field_details #no field mappings details for this query object,"
                f"{mapping_query_object}")
            return {'detail': 'Mapping for the details provided does not exist'}
        else:
            logger.info(
                f"#ui_apis.py  #get_field_mappings #get_field_details #fetched mapping_json details,"
                f"mapping_json:{mapping_json}")

            mapping_json = await sort_dict(mapping_json)
            mapping_response = {
                "entity": entity,
                "source": source,
                "destination": destination,
                "mapping": mapping_json
            }
            return mapping_response

    except Exception as e:
        logger.error(f"#ui_apis.py  #get_field_mappings #exception_getting_field_mappings  #Exception, {e}",
                     exc_info=True)


async def get_mapping_details(db: Session):

    try:
        entities = [ "application", "candidate", "job"]
        mapping_query_object = {}
        get_fields = [models.Mapping.destination,models.Mapping.source]
        all_ats = await  get_all_field_details(db, models.Company, mapping_query_object, *get_fields)
        destination_set = set()
        source_set = set()
        for ats in all_ats:
            destination_set.add(str(ats[0]))
            source_set.add(str(ats[1]))
        logger.info(
            f"#ui_apis.py  #get_mapping_details #get_all_ats_details_in_rds #Successfully fetched all ATS detals")
        destinations = list(destination_set)
        sources = list(source_set)
        mapping_response = {
            "entities":entities,
            "destinations": destinations,
            "sources": sources,
        }
        return mapping_response

    except Exception as e:
        logger.error(f"#ui_apis.py  #get_mapping_details #exception_getting_get_mapping_details  #Exception, {e}",
                     exc_info=True)

async def get_field_keys(db: Session, request: dict):
    entity = request.query_params.get("entity",None)
    source = request.query_params.get("source", None)
    destination = request.query_params.get("destination", None)
    logger.info(
        f"#ui_apis.py  #get_field_keys #query_field_keys #query_field_keys_details,entity:{entity},"
        f" source:{source}, destination:{destination}")
    query_object = {
        "entity": entity,
    }

    if source:
        validation_list = [{
            "field": "entity",
            "alias": "Entity"
        }, {
            "field": "source",
            "alias": "Source"
        },
        ]
        query_object["source"] = source
    elif destination:
        validation_list = [{
            "field": "entity",
            "alias": "Entity"
        }, {
            "field": "destination",
            "alias": "Destination"
        }
        ]
        query_object["destination"] = destination
    else:
        return {'detail': 'Source and Destination is not provided'}
    logger.info(
        f"#ui_apis.py  #get_field_keys #query_field_keys #validation_query_object,query_object:{query_object}")
    messages = field_validation(query_object, validation_list)
    if messages:
        return JSONResponse(content={"detail": messages}, status_code=400)
    try:
        if destination:
            field_keys = ATS_FIELDS.get(destination).get(entity).get("destination")
        elif source:
            field_keys = ATS_FIELDS.get(source).get(entity).get("source")
        else:
            return {'detail': 'Source or Destination is not provided'}

        field_keys_list = []
        if field_keys:
            field_keys_list = [{"name":name, "type":type} for name,type in field_keys]
        return field_keys_list

    except Exception as e:
        logger.error(f"#ui_apis.py  #get_field_mappings #exception_getting_field_mappings  #Exception, {e}",
                     exc_info=True)
        error = f"No field keys were found for the given details"
        return JSONResponse(content={"detail": error}, status_code=400)

async def post_field_mappings(db: Session, request: dict):
    validation_list = [{
        "field": "destination",
        "alias": "Destination"
    },{
        "field": "entity",
        "alias": "Entity"
    },{
        "field": "source",
        "alias": "Source"
    }]
    messages = field_validation(request, validation_list)
    if messages:
        return JSONResponse(content={"detail": messages}, status_code=400)
    try:
        destination = request.get("destination")
        entity = request.get("entity")
        source = request.get("source")
        mapping = request.get("mapping", None)
        if mapping is None:
            return {'detail': 'Field mapping is not provided'}
        dict_validation_messages = dict_field_validation(mapping)
        if dict_validation_messages:
            logger.info(
                f"#ui_apis.py  #post_field_mappings #mapping_field_value_empty #mapping json value field is empty, "
                f"{dict_validation_messages}")

            return JSONResponse(content={"detail": dict_validation_messages}, status_code=400)

        # get mapping_json from mapping rds table
        mapping_query_object = {
            "source": source,
            "destination": destination,
            "entity": entity
        }
        mapping_json = await get_field_details(db, models.Mapping, mapping_query_object, "mapping")

        if mapping_json is None:
            logger.info(
                f"#ui_apis.py  #post_field_mappings #get_field_details #no field mappings details for this query object,"
                f"{mapping_query_object}")
            mapping_query_object["mapping"] = request.get("mapping")
            await create_field_details(db, models.Mapping, mapping_query_object)
            logger.info(
                f"#ui_apis.py  #post_field_mappings #create_field_details #successfully created mapping_json,"
                f"{mapping_query_object}")
            return {'detail': 'Mapping created successfully in the rds'}
        else:
            # #update request
            update_object = {"mapping": mapping}
            await update_field_details(db, models.Mapping, mapping_query_object, update_object)
            logger.info(
                f"#ui_apis.py  #post_field_mappings #get_field_details #fetched mapping_json details and updated with,"
                f"update_object:{update_object}")
            return {'detail': 'Mapping updated successfully in the rds'}

    except Exception as e:
        logger.error(f"#ui_apis.py  #get_ui_field_mappings #exception_getting_ui_field_mappings  #Exception, {e}",
                     exc_info=True)