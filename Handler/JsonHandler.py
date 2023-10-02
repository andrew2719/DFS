import json

async def convert_json_to_dict(json_string):
    return json.loads(json_string)

async def convert_dict_to_json(dict):
    return json.dumps(dict)

async def acknowledgment(bool,extras = None):

    response = {
        'status':bool,
        'extras':extras
    }

    return await convert_dict_to_json(response)
