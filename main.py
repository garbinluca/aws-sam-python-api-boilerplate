import repository
import helpers


def index(event, context):
    records = repository.get_last_records()
    return helpers.json_success(records)


def show(event, context):
    record_id = event['pathParameters']['id']
    record = repository.show(record_id)
    return helpers.json_success(record)


def create(event, context):
    body = json.loads(event['body'])
    record = repository.create(body)
    return helpers.json_success(record)


def update(event, context):
    record_id = event['pathParameters']['id']
    body = json.loads(event['body'])
    record = repository.update(record_id, body)
    return helpers.json_success(record)


def delete(event, context):
    record_id = event['pathParameters']['id']
    record = repository.delete(record_id)
    return helpers.json_success(record)
