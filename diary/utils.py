import json


def clean_json_value(value):
    # Known types to convert to string:
    #   - datetime
    try:
        json.dumps(dict(key=value))
    except (TypeError, ValueError):
        return str(value)

    return value


def clean_json(data):
    for key, value in data.iteritems():
        if isinstance(value, dict):
            data[key] = clean_json(value)
        elif isinstance(value, (list, tuple)):
            data[key] = [clean_json_value(item) for item in value]
        else:
            data[key] = clean_json_value(value)
    return data


def print_header(logger, title, meth=None):
    if meth is None:
        meth = logger.info
    meth('======== %s ========', title)


def print_json(logger, data, meth=None):
    if meth is None:
        meth = logger.info
    meth(json.dumps(clean_json(data), indent=4))
