def json_success(response, code = 200):

    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response, default=str)
    }
