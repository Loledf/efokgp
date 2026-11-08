import re, subprocess
from flask import Flask, request, Response, send_from_directory

app = Flask(__name__)
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')

def run(cmd, timeout=170):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        return ANSI.sub('', p.stdout + '\n' + p.stderr)
    except subprocess.TimeoutExpired:
        return ''
    except FileNotFoundError:
        return None

def reply(text):
    if text is None:
        return Response('{"error":"утилита не найдена на сервере"}', 500, mimetype='application/json')
    return Response(text, mimetype='text/plain; charset=utf-8')

@app.after_request
def cors(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r

def username():
    u = request.args.get('username', '')
    return u if re.fullmatch(r'[\w.\-]{1,64}', u) else None

@app.get('/')
def index():
    return send_from_directory('.', 'test.html')

@app.get('/sherlock')
def sherlock():
    u = username()
    if not u: return Response('bad username', 400)
    return reply(run(['sherlock', '--print-found', '--timeout', '10', u]))

@app.get('/maigret')
def maigret():
    u = username()
    if not u: return Response('bad username', 400)
    return reply(run(['maigret', u, '--timeout', '10']))

@app.get('/phoneinfoga')
def phoneinfoga():
    n = request.args.get('number', '')
    if not re.fullmatch(r'\+?\d{6,15}', n): return Response('bad number', 400)
    return reply(run(['docker', 'run', '--rm', 'sundowndev/phoneinfoga:latest', 'scan', '-n', n]))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8787)