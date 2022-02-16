#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import requests
import signal
import sys
from pathlib import Path
import socketserver
import http.server
from urllib.parse import parse_qs, urlparse
import threading

DUMMY_PORT = 8000
RUNTIME_PORT = 9001
RUNTIME_ADDRESS = "127.0.0.1"

# global variables
# extension name has to match the file's parent directory name)
LAMBDA_EXTENSION_NAME = Path(__file__).parent.name

class RequestHandler(http.server.BaseHTTPRequestHandler, object):
    def do_GET(self):
        print('path = {}'.format(self.path))

        parsed_path = urlparse(self.path)
        print('parsed: path = {}, query = {}'.format(parsed_path.path, parse_qs(parsed_path.query)))

        print('headers\r\n-----\r\n{}-----'.format(self.headers))
       
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_GET')

    def do_POST(self):
        print('path = {}'.format(self.path))

        parsed_path = urlparse(self.path)
        print('parsed: path = {}, query = {}'.format(parsed_path.path, parse_qs(parsed_path.query)))

        print('headers\r\n-----\r\n{}-----'.format(self.headers))

        content_length = int(self.headers['content-length'])
        
        print('body = {}'.format(self.rfile.read(content_length).decode('utf-8')))
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello from do_POST')

        
        
def run():
    with socketserver.TCPServer((RUNTIME_ADDRESS, DUMMY_PORT), RequestHandler) as httpd:
        print("serving at port", DUMMY_PORT)
        httpd.serve_forever()
        httpd.handle_request()

# custom extension code
def execute_custom_processing(event):
    # perform custom per-event processing here
    print(f"[{LAMBDA_EXTENSION_NAME}] Received event: {json.dumps(event)}", flush=True)


# boiler plate code
def handle_signal(signal, frame):
    # if needed pass this signal down to child processes
    print(f"[{LAMBDA_EXTENSION_NAME}] Received signal={signal}. Exiting.", flush=True)
    sys.exit(0)


def register_extension():
    print(f"[{LAMBDA_EXTENSION_NAME}] Registering...", flush=True)
    headers = {
        'Lambda-Extension-Name': LAMBDA_EXTENSION_NAME,
    }
    payload = {
        'events': [
            'INVOKE',
            'SHUTDOWN'
        ],
    }
    response = requests.post(
        url=f"http://{os.environ['AWS_LAMBDA_RUNTIME_API']}/2020-01-01/extension/register",
        json=payload,
        headers=headers
    )
    ext_id = response.headers['Lambda-Extension-Identifier']
    print(f"[{LAMBDA_EXTENSION_NAME}] Registered with ID: {ext_id}", flush=True)

    return ext_id


def process_events(ext_id):
    thread1 = threading.Thread(target=run)
    thread1.start()

    headers = {
        'Lambda-Extension-Identifier': ext_id
    }
    while True:
        os.environ['AWS_LAMBDA_RUNTIME_API'] = RUNTIME_ADDRESS + ':' + str(RUNTIME_PORT)
        print(f"[{LAMBDA_EXTENSION_NAME}] Waiting for event...", flush=True)
        response = requests.get(
            url=f"http://{os.environ['AWS_LAMBDA_RUNTIME_API']}/2020-01-01/extension/event/next",
            headers=headers,
            timeout=None
        )
        event = json.loads(response.text)
        print('@@@@@@@@@@@@@@@@@@@@@@')
        print(response.text)
        print('@@@@@@@@@@@@@@@@@@@@@@')
        if event['eventType'] == 'SHUTDOWN':
            print(f"[{LAMBDA_EXTENSION_NAME}] Received SHUTDOWN event. Exiting.", flush=True)
            sys.exit(0)
        else:
            send_response(event['requestId'])
            execute_custom_processing(event)

def send_response(requestId):
    data = {
        "statusCode": 500,
        "body": json.dumps({
            "message": "chaos!!"
        }),
    }
    response = requests.post(
        url=f"http://{os.environ['AWS_LAMBDA_RUNTIME_API']}/2018-06-01/runtime/invocation/" + requestId + '/response',
        data=data,
        timeout=None
    )
    os.environ['AWS_LAMBDA_RUNTIME_API'] = RUNTIME_ADDRESS + ':' + str(DUMMY_PORT)

def main():
    # handle signals
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # execute extensions logic
    extension_id = register_extension()
    process_events(extension_id)


if __name__ == "__main__":
    main()
