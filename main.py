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