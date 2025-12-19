"""
Netlify serverless function handler
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import app

def handler(event, context):
    """
    Netlify serverless function handler
    Converts Netlify event to WSGI and calls Flask app
    """
    from io import BytesIO
    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import WSGIRequestHandler
    
    # Create WSGI environ from Netlify event
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'PATH_INFO': event.get('path', '/'),
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(event.get('body', '').encode() if event.get('body') else b''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add query string
    if event.get('queryStringParameters'):
        qs = '&'.join([f'{k}={v}' for k, v in event['queryStringParameters'].items()])
        environ['QUERY_STRING'] = qs
    
    # Add headers
    for key, value in (event.get('headers') or {}).items():
        header_name = key.upper().replace('-', '_')
        if header_name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            header_name = f'HTTP_{header_name}'
        environ[header_name] = value
    
    # Call Flask app
    with app.app_context():
        response = app(environ, lambda status, headers: None)
        
        # Get response body
        body_parts = []
        for part in response:
            if isinstance(part, bytes):
                body_parts.append(part)
            else:
                body_parts.append(part.encode('utf-8'))
        
        body = b''.join(body_parts).decode('utf-8')
        
        # Get status code
        status_code = 200
        if hasattr(response, 'status_code'):
            status_code = response.status_code
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8'
            },
            'body': body
        }


