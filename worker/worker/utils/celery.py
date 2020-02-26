import base64
from collections import defaultdict

from flask import json

from worker.utils.helpers import (pop_app_context_if_pushed,
                                  push_app_context_if_has_not_app_context)


def get_operations_in_queue(*queues) -> tuple:
    ops = list()
    discoveries = defaultdict(bool)
    backups = defaultdict(bool)
    restores = defaultdict(bool)

    from worker import celery
    with celery.pool.acquire(block=True) as conn:
        for queue in queues:
            r = conn.default_channel.client.lrange(queue, 0, -1)
            ops += r

    for op in ops:
        j = json.loads(op)

        try:
            body = json.loads(base64.b64decode(j["body"]))[1]

            discovery_id = body.get("disovery_id", None)
            if discovery_id is not None:
                discoveries[discovery_id] = True

            device_id = body.get("device_id", None)
            if device_id is not None:
                backups[device_id] = True

            backup_id = body.get("backup_id", None)
            if backup_id is not None:
                restores[backup_id] = True
        except Exception:
            continue

    return discoveries, backups, restores


def clean_operation_statuses():
    is_pushed = push_app_context_if_has_not_app_context()

    from worker import db
    from worker.database.models import Device
    from worker.database.models import Discovery

    discoveries = db.session.query(Discovery).all()
    devices = db.session.query(Device).all()

    q_discoveries, q_backups, q_restores = \
        get_operations_in_queue("foreground", "background")

    for discovery in discoveries:
        if q_discoveries[discovery.ident] is False:
            discovery.operation_status = "finish"
        else:
            discovery.operation_status = "start"

    for device in devices:
        if q_backups[device.ident] is False:
            device.backup_process_status = "finish"

        if q_restores[device.ident] is False:
            device.restore_process_status = "finish"

    db.session.commit()

    pop_app_context_if_pushed(is_pushed)
