import time

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

thread = None
thread_lock = Lock()

control = RobotControl("10.0.0.63")


def background_task():
    global control

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
        print(f'Move robot forward for {timer} seconds')
        control.robot_forward(timer)

    return  "Success"   


@app.route("/left", methods = ['POST']) 
def left(): 
    global control

    if request.method == 'POST':
        print(request.json)
        timer = request.json['time']
        print(f'Move robot left for {timer} seconds')
        control.robot_rotate_left(timer)

    return  "Success"  

@app.route("/right", methods = ['POST']) 
def right(): 
    global control

    if request.method == 'POST':
        print(request.json)
        timer = request.json['time']
        print(f'Move robot right for {timer} seconds')
        control.robot_rotate_right(timer)

    return  "Success"  

@app.route("/finished", methods = ['GET']) 
def finished(): 
    global control

    finished=control.is_finished()

    print(f'Finished: {finished}')
    return jsonify(
        finished=finished
    )

@app.route("/detect", methods = ['GET']) 
def detected(): 
    global control

    detected=control.robot_detect_obstacle()

    return jsonify(
        detected=detected
    )

    

if __name__ == '__main__':
    sio.run(app)
