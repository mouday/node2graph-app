import os
from flask_cors import CORS
from flask import Flask, request, make_response, send_file
from uuid import uuid4

import subprocess

app = Flask(__name__, static_url_path='/', static_folder='static')
CORS(app, supports_credentials=True)

UPLOAD_DIR_PATH = os.path.join(app.root_path, app.static_folder, 'upload')
UPLOAD_DIR_URL = '/upload'
print(UPLOAD_DIR_URL)

def make_error(msg='error', code=-1):
    return {
        'msg': msg,
        'code': code,
        'data': None
    }


@app.get('/')
def index():
    return send_file('static/index.html')


@app.post('/convertNodeToPng')
def convert_node_to_png():
    data = request.json['data']
    img_format = request.json.get('img_format') or 'svg'
    if not data:
        return make_error('data is empty')

    data_uid = uuid4().hex
    fullname = os.path.join(UPLOAD_DIR_PATH, "{}.node".format(data_uid))
    if not os.path.exists(UPLOAD_DIR_PATH):
        os.makedirs(UPLOAD_DIR_PATH)

    with open(fullname, "w") as f:
        f.write(data)

    fullname = os.path.join(UPLOAD_DIR_PATH, "{}.node".format(data_uid))
    if not os.path.exists(fullname):
        return make_error()

    result = subprocess.run(['pg_node2graph', '--remove-dots', '--color', '-T', img_format, fullname],
                            capture_output=True, text=True)

    if result.returncode != 0:
        return make_error(result.stderr)

    old_node_name = "{}.node.{}".format(data_uid, img_format)
    new_node_name = "{}.{}".format(data_uid, img_format)

    os.rename(
        os.path.join(UPLOAD_DIR_PATH, old_node_name),
        os.path.join(UPLOAD_DIR_PATH, new_node_name)
    )

    return {
        'msg': 'success',
        'code': 0,
        'data': {
            "img_url": "{}/{}".format(UPLOAD_DIR_URL, new_node_name)
        }
    }


if __name__ == "__main__":
    app.run(debug=False)
