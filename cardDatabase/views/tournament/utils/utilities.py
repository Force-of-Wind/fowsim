def check_value_is_meta_data(name, default_meta_data_fields):
    for field in default_meta_data_fields:
        if field['name'] == name:
            return True
    return False

def map_meta_data(name, value, default_meta_data_fields):
    for field in default_meta_data_fields:
        if field['name'] == name:
            field['value'] = value
            return field
    return None

def any_empty(*args):
    return any(not arg for arg in args)