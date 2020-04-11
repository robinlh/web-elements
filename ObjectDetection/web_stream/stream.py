import argparse
import datetime
import threading
import time

import cv2
import imutils
from flask import Flask
from flask import Response
from flask import render_template
from imutils.video import VideoStream
from motion_detector import MotionDetector
from telegram_poster import Telegram

# initialize output frame and a lock for thread safety
outputFrame = None
lock = threading.Lock()

# initialize a flask obj
app = Flask(__name__)

# initialize telegram obj
bot_token = <bot_token>
bot_id = <bot_id>
telegram_bot = Telegram(bot_token, bot_id)
motion_detected = False

# initialize video stream
# vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
    return render_template("index.html")

def detect_motion(frameCount):
    global vs, outputFrame, lock, motion_detected

    # initialize the motion detector tot frames
    md = MotionDetector(accumWeight=0.1)
    total = 0

    while True:
        # read next frame from stream, resize, to grayscale, blur
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # timestamp on image
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # if tot frames reached enough to construct background model, continue

        if total > frameCount:

            # detect
            motion = md.detect(gray)

            # check if motion was found
            if motion is not None:
                # draw bounding box
                (thresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)

                if motion_detected is False:
                    res = telegram_bot.telegram_bot_sendtext("motion detected: " + timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"))
                    print(res)
                    motion_detected = True


        # update background model and increment total frames
        md.update(gray)
        total += 1

        # acquire the lock, set output frame, release
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global ref to output frame and lock vars
    global outputFrame, lock

    # frames from output stream
    while True:
        # acquire lock
        with lock:
            # skip unavailable frame
            if outputFrame is None:
                continue

            # encode
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated and media type
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    # arg parser for cl args and some extra info
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # start thread
    t = threading.Thread(target=detect_motion, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    # flask
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

# release video stream pointer
vs.stop()
