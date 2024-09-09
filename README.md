# goit-pyweb-04

**TASK**

*Structure*
```
|- static/
| |- style.css
| |- logo.png
|- storage/
|   |_ data.json
|- templates/
|  |- index.html
|  |- message.html
|  |_ error.html
|_ main.py
```

***main.py***

PS: code was noted in vietnamese.
Changed the directory for logo.png and style.css in all ".html" files

```
import json
import os
import socket
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

STORAGE_DIR = 'storage'
DATA_FILE = os.path.join(STORAGE_DIR, 'data.json')

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message.html')
def message():
    return render_template('message.html')

@app.route('/message', methods=['POST'])
def postmessage():
    # Lấy dữ liệu từ form
    username = request.form.get('username')
    message = request.form.get('message')

    # Gửi dữ liệu qua socket
    send_message_via_socket(username, message)

    # Chuyển hướng về trang chủ
    return redirect(url_for('index'))

def send_message_via_socket(username, message):
    # Tạo socket và gửi dữ liệu
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = json.dumps({'username': username, 'message': message}).encode('utf-8')
    sock.sendto(data, ('localhost', 5000))
    sock.close()  # Đảm bảo đóng socket sau khi gửi

def save_message_to_file(username, message):
    # Đọc dữ liệu hiện có từ file
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as file:
            json.dump({}, file)

    with open(DATA_FILE, 'r+') as file:
        try:
            data_store = json.load(file)
        except json.JSONDecodeError:
            data_store = {}

        # Thêm thông tin tin nhắn mới
        timestamp = str(datetime.now())
        data_store[timestamp] = {'username': username, 'message': message}

        # Ghi lại vào file
        file.seek(0)
        json.dump(data_store, file, indent=4)
        file.truncate()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def run_socket_server():
    # Thiết lập socket server để nhận dữ liệu
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 5000))

    while True:
        # Nhận dữ liệu từ socket
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))

        # Lấy username và message từ dữ liệu nhận được
        username = message.get('username')
        msg = message.get('message')

        # Lưu dữ liệu vào file JSON
        save_message_to_file(username, msg)

if __name__ == '__main__':
    # Tạo và khởi động thread cho socket server
    socket_thread = threading.Thread(target=run_socket_server)
    socket_thread.daemon = True
    socket_thread.start()

    app.run(port=3000, debug=True)
```

**ADDITIONAL TASK**

Я пробывал запустить сайт через Docker, не скольками способами: заменяя разными портами, но всеравно не запускается. Выводит oшибку низже(с разными портами(призамене)):

```
Restarting with stat
 Exception in thread Thread-1 (run_socket_server):
 Traceback (most recent call last):
  File "/usr/local/lib/python3.12/threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "/usr/local/lib/python3.12/threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "/app/main.py", line 73, in run_socket_server
    sock.bind(('localhost', 5000))
OSError: [Errno 98] Address already in use
```
