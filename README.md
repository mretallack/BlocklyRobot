# BlocklyRobot

A Blockly-based visual programming interface for controlling a smart robot car over WiFi.

## Requirements

- Linux
- Python 3.x
- Flask
- Flask-SocketIO

## Installation

Install Python dependencies:
```bash
pip install flask flask-socketio
```

## Configuration

Edit `robot_control.py` and set your robot's IP address:
```python
control = RobotControl("10.0.0.57")  # Change to your robot's IP
```

## Usage

Start the server:
```bash
make
```

The web interface will be available at `http://localhost:5000`

## Features

### Robot Movement
- **Move Forward/Backward**: Move robot for specified seconds
- **Rotate Left/Right**: Rotate robot for specified seconds
- **Obstacle Detection**: Automatically stops movement when obstacle detected within 20cm

### Camera Control
- **Pan Left/Right**: Pan camera by specified count
- **Center Camera**: Reset camera to center position
- **Obstacle Detection**: Check for obstacles after camera movement

### Programming
- Visual Blockly interface with drag-and-drop blocks
- Standard logic, loops, math, and text blocks
- Robot-specific control blocks
- Save/load programs
- Continuous execution loop (runs every second)

## Architecture

- **robot.py**: Flask web server with command queue for serialized execution
- **robot_control.py**: Robot control class handling TCP communication on port 100
- **static/engine.js**: Blockly interface with async/await for responsive UI
- **templates/index.html**: Web interface with Blockly editor

## Robot Protocol

Commands sent as JSON over TCP:
- Movement: `{"H": 22, "N": 3, "D1": direction, "D2": speed}`
- Obstacle detection: `{"H": 22, "N": 21, "D1": 1}`
- Camera control: `{"H": 22, "N": 106, "D1": direction}`
- Stop: `{"N": 100}`

Directions:
- Movement: 1=left, 2=right, 3=forward, 4=backward
- Camera: 1=tilt_down, 2=tilt_up, 3=pan_right, 4=pan_left, 5=center
