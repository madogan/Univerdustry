import requestsfrom application.utils.helpers import get_configdef insert_one(collection_name, document):    url = get_config("MONGO_REST")    url += f'/{collection_name}/insert/one'    result = requests.post(        url=url,        json={"document": document}    )    return result.json()def find(collection_name, data):    url = get_config("MONGO_REST")    url += f'/{collection_name}/find'    result = requests.get(        url=url,        json=data or dict()    )    return result.json()def create_index(collection_name, keys, name, background=True, unique=True,                 sparse=True):    url = get_config("MONGO_REST")    url += f'/{collection_name}/create/index'    requests.post(url, json={        "keys": keys,        "name": name,        "background": background,        "unique": unique,        "sparse": sparse    })