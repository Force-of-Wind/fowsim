import copy


def check_value_is_meta_data(name, default_meta_data_fields):
    for field in default_meta_data_fields:
        if field["name"] == name:
            return True
    return False


def map_meta_data(name, value, default_meta_data_fields):
    default_fields = copy.deepcopy(default_meta_data_fields)
    for field in default_fields:
        if field["name"] == name:
            field["value"] = value
            return field
    return None


def any_empty(*args):
    return any(not arg for arg in args)


def ensure_meta_field(meta_data, default_meta_data_fields, name):
    """Return a copy of meta_data guaranteed to contain a field named `name`.

    If the field is missing (e.g. a legacy tournament saved before that field
    existed) the default definition is appended with an empty value. This lets
    the edit form render newer fields - like the venue map coordinates - for
    older tournaments without altering any of their existing data."""
    result = copy.deepcopy(meta_data) if meta_data else []
    if any(field.get("name") == name for field in result):
        return result
    for default_field in default_meta_data_fields:
        if default_field["name"] == name:
            new_field = copy.deepcopy(default_field)
            new_field["value"] = ""
            result.append(new_field)
            break
    return result
