import json
import subprocess
import time

def lambda_handler(event, context):
    # command(['ls','-la', '/opt/extensions'])
    # command(['ls','-la', '/opt/python-extension'])

    time.sleep(2)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world"
        }),
    }

def command(cmd):
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    print(out.stdout.decode())