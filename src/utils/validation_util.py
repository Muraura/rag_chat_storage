from datetime import datetime
def field_validation(request_data, field_list):
    messages = []
    for field in field_list:
        field_name = field.get("field")
        field_alias = field.get("alias")
        if field_name in request_data:
            if not request_data[field_name]:
                messages.append(field_alias + " is empty.")
        else:
            messages.append(field_alias + " is missing.")
    return messages


def dict_field_validation(item_dict):
    messages = []
    for item in item_dict:
        if not item:
            messages.append(item_dict[item] + " key is empty.")
        if not item_dict[item]:
            messages.append(item + " value is empty.")
    return messages


def date_format_validation(request_data):
    messages = []
    for field in request_data:
        field_name = field.get("field")
        field_alias = field.get("alias")

        if field_name:
            try:
                date_obj = datetime.strptime(field_name, "%Y-%m-%dT%H:%M:%S")
                expected_format = date_obj.strftime("%Y-%m-%dT%H:%M:%S")

                if field_name != expected_format:
                    messages.append(f"Invalid date format for {field_alias}. Expected format: {expected_format}")

            except ValueError:
                messages.append(f"Invalid date format for {field_alias}")

        else:
            messages.append(f"Missing {field_alias}")

    return messages


def date_order_validation(from_date, to_date):
    messages = []
    if from_date >= to_date:
        messages.append("The From date should be less than the To date")
    return messages

