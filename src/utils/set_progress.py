import json


def set_progress(uuid, status, progress, redis_client=None):
    if redis_client is None:
        raise ValueError('Redis is not initialized')

    return redis_client.set(
        uuid,
        json.dumps({
            'status': status,
            'progress': progress
        }, ensure_ascii=False),
        ex=3600
    )