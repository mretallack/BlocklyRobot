import time
import queue
import threading

from threading import Lock
from flask import Flask , jsonify
from flask import render_template 
from flask import request, jsonify
from flask_socketio import SocketIO

from robot_control import RobotControl

# creates a Flask application 
app = Flask(__name__) 
app.secret_key = 'your secret here'
sio = SocketIO(app)


# define the queue for the commands
command_queue = queue.Queue()
command_lock = Lock()
command_executing = False

thread = None
thread_lock = Lock()

control = RobotControl("10.0.0.57")

def command_worker():
    """Worker thread to process commands sequentially"""
    global command_executing
    while True:
        try:
            cmd_func, args, kwargs = command_queue.get(timeout=1)
            command_executing = True
            with command_lock:
                cmd_func(*args, **kwargs)
            command_executing = False
            command_queue.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error executing command: {e}")
            command_executing = False
            command_queue.task_done()


def background_task():
    global control
    # Start command worker thread
    worker = threading.Thread(target=command_worker, daemon=True)
    worker.start()
    #control.main_loop()


@app.route("/") 
def hello(): 
    global thread
    with thread_lock:
        if thread is None:
            thread = sio.start_background_task(background_task)

    message = "Hello, World"
    return render_template('index.html',  
                           message=message) 
  

@app.route("/script", methods = ['GET', 'PUT']) 
def script(): 

    result=None

    if request.method == 'PUT':
        print(request.data)
        with open("saved.xml", mode="w") as f:
            f.write(request.data.decode('utf-8'))
            f.close()
        result="Success"
    else:

        with open("saved.xml", mode="r") as f:
            result=f.read()
            f.close()

    return result


# register the /forward flask endpoint to handle in form data
# and get the time field
@app.route("/forward", methods = ['POST']) 
def forward(): 
    global control

    if request.method == 'POST':
        print(request.json)
        timer = request.json['time']
        print(f'Queueing: Move robot forward for {timer} seconds')
        command_queue.put((control.robot_forward, (timer,), {}))

    return  "Success"   


@app.route("/backward", methods = ['POST']) 
def backward(): 
    global control

    if request.method == 'POST':
        print(request.json)
        timer = request.json['time']
        print(f'Queueing: Move robot backward for {timer} seconds')
        command_queue.put((control.robot_backward, (timer,), {}))

    return  "Success"  

@app.route("/left", methods = ['POST']) 
def left(): 
    global control

    if request.method == 'POST':
        print(request.json)
        timer = request.json['time']
        print(f'Queueing: Move robot left for {timer} seconds')
        command_queue.put((control.robot_rotate_left, (timer,), {}))

    return  "Success"  

@app.route("/right", methods = ['POST']) 
def right(): 
    global control

    if request.method == 'POST':
        print(request.json)
        timer = request.json['time']
        print(f'Queueing: Move robot right for {timer} seconds')
        command_queue.put((control.robot_rotate_right, (timer,), {}))

    return  "Success"  

@app.route("/finished", methods = ['GET']) 
def finished(): 
    global control, command_executing

    finished = not command_executing and command_queue.empty() and control.is_finished()

    print(f'Finished: {finished}')
    return jsonify(
        finished=finished
    )

@app.route("/queue_empty", methods = ['GET']) 
def queue_empty(): 
    empty = command_queue.empty()
    return jsonify(
        empty=empty
    )

@app.route("/detect", methods = ['GET']) 
def detected(): 
    global control

    detected=control.robot_detect_obstacle()

    return jsonify(
        detected=detected
    )

@app.route("/camera_pan_left", methods = ['POST']) 
def camera_pan_left(): 
    global control
    if request.method == 'POST':
        count = request.json.get('count', 1)
        print(f'Queueing: Pan camera left {count} times')
        command_queue.put((control.robot_camera_pan_left, (count,), {}))
    return "Success"

@app.route("/camera_pan_right", methods = ['POST']) 
def camera_pan_right(): 
    global control
    if request.method == 'POST':
        count = request.json.get('count', 1)
        print(f'Queueing: Pan camera right {count} times')
        command_queue.put((control.robot_camera_pan_right, (count,), {}))
    return "Success"

@app.route("/camera_center", methods = ['POST']) 
def camera_center(): 
    global control
    print('Queueing: Center camera')
    command_queue.put((control.robot_camera_control, (5,), {}))
    return "Success"

    

if __name__ == '__main__':
    sio.run(app)
