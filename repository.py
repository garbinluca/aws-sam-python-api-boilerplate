import boto3
import requests
import json
import uuid

from collections import defaultdict
from operator import itemgetter
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ExampleTableName')


###
# Create update body for DynamoDB
###
def prepare_update(body, updatable_fields):
    update_expression = 'SET '
    expression_values = {}

    for field in updatable_fields:
        update_expression += f'#{field} = :{field}, '
        expression_values[f':{field}'] = body[field]

    # Rimuovi l'ultima virgola e spazio
    update_expression = update_expression[:-2]

    # Crea il dizionario per i nomi degli attributi
    expression_names = {f'#{field}': field for field in updatable_fields if field in body}

    return {
        'update_expression': update_expression,
        'expression_values': expression_values,
        'expression_names': expression_names
    }


###
# Get last n records
# -1 => all
###
def get_last_records(max_records: int = -1):
    response = table.scan()
    items = response['Items']

    # Continua la scan se ci sono più risultati
    if 'LastEvaluatedKey' in response:
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
            if 0 < max_records < len(items) + len(response['Items']):
                max_items = len(items) + len(response['Items']) - max_records
                items.extend(response['Items'][0:max_items])
            else:
                items.extend(response['Items'])

    return items


###
# Get records by date
###
def get_by_date(date: str):
    response = table.query(
        IndexName='ExampleTableName-day-index',
        KeyConditionExpression='#created_at = :created_at',
        ScanIndexForward=False,
        ExpressionAttributeNames={
            '#created_at': 'created_at'
        },
        ExpressionAttributeValues={
            ':created_at': date
        }
    )
    return response['Items']


###
# New record
###
def create(body):

    # body = json.loads(event['body'])
    text = body['text']
    date = body['date']
    id = uuid.uuid1()
    created_at = datetime.now()

    new_record = {
        'id': str(id),
        'date': date,
        'text': text,
        'created_at': str(created_at)
    }

    table.put_item(Item=new_record)

    return new_record


###
# Get record by id
###
def show(record_id):

    response = table.get_item(
        Key={'id': record_id}
    )

    if 'Item' not in response:
        raise Exception('Workout non trovato')

    return response['Item']


###
# Update record
###
def update(record_id, body):

    # recordId = event['pathParameters']['id']
    # body = json.loads(event['body'])

    update = prepare_update(body, ['text', 'date', 'count'])

    table.update_item(
        Key={'id': record_id},
        UpdateExpression=update['update_expression'],
        ExpressionAttributeValues=update['expression_values'],
        ExpressionAttributeNames=update['expression_names'],
        ReturnValues='ALL_NEW'
    )

    return show(record_id)


###
# Delete record
###
def delete(record_id):

    record = show(record_id)

    table.delete_item(
        Key={'id': record_id},
    )

    return record
