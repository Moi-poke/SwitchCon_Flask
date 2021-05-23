import time

from flask import Flask, render_template, request, jsonify, Response
import json
import os
# from importlib import import_module
# import requests
# import pandas as pd
# import numpy as np
# from scipy.stats import chi2_contingency
import serial

import SWLogger
from camera import Camera

logger = SWLogger.root_logger()

app = Flask(__name__)

button = ["Y", "B", "A", "X", "L", "R", "ZL", "ZR", "MINUS", "PLUS", "LCLICK", "RCLICK", "HOME", "CAPTURE"]
Buttons = [2 ** (i + 2) for i in range(14)]

portNum = 3  # ポート番号の設定
camera_id = 4  # カメラIDの設定

# シリアル接続
if os.name == 'nt':
    ser = serial.Serial("COM" + str(portNum), 9600)
elif os.name == 'posix':
    ser = serial.Serial("/dev/ttyUSB" + str(portNum), 9600)

neutral = '0 8 80 80 80 80'  # 無操作状態. "Button Hat Lstick_x Lstick_y Rstick_x Rstick_y"で並んでいる。


@app.route('/', methods=["GET", "POST"])
def check():
    return render_template('index.html', input_list=button)


@app.route('/send', methods=['POST'])
def send():
    # json形式でURLを受け取る
    p = Buttons[button.index(request.json['button'])]  # 3

    return_data = {"button": p}
    row = format(p, '#06x') + ' 8 80 80 80 80'  # ボタン操作のみを考慮
    logger.debug(row)
    # print(locals())

    # 0.1秒間指定されたボタンを押下
    ser.write((row + '\r\n').encode('utf-8'))
    time.sleep(0.1)
    ser.write((neutral + '\r\n').encode('utf-8'))

    return jsonify(ResultSet=json.dumps(return_data))


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(camera_id)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888, threaded=True)
