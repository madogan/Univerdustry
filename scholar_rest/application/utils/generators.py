from _md5 import md5


def generate_task_id(resource_id, operation_name):
    return md5((str(resource_id) + str(operation_name)).encode("utf-8"))\
        .hexdigest()
