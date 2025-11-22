import time
import socket
import json

class RobotControl():
    
    
    def __init__(self, robot_ip):
        self.robot_ip=robot_ip
        self.running=False
        self.obstacle_stopped=False
        pass

    def robot_connect(self):
    
        self.running=True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.robot_ip, 100)) 
        
        s.settimeout(0.1)
        return(s)
    
    def robot_heatbeat(self, s, count, callback=None):
    
        count_complete=True
        count=int(count)*10
        buffer = ""
        
        while True:
            
            try:
            
                data = s.recv(1024)
                if data:
                    
                    data = data.decode("utf-8")
                    buffer += data
                    
                    # Process complete messages
                    while "}" in buffer:
                        end_pos = buffer.find("}")
                        message = buffer[:end_pos+1]
                        buffer = buffer[end_pos+1:]
                        
                        if message == "{Heartbeat}":
                            print("Got Heartbeat, sending...")
                            s.sendall("{Heartbeat}".encode('utf-8'))

                        if callback!=None:
                            res=callback(message)
                            # if the callback fails, return false
                            if res==False:
                                # tell the caller that the count did not complete
                                count_complete=False
                                return count_complete  # Exit immediately
                        
            except socket.timeout as e:
                pass
            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"Connection error: {e}")
                return False
            
            count=count-1
            
            if count<=0:
                break;

        return(count_complete)
            
    def robot_all_stop(self, s):
        
        try:
            tosend={ "N":100}
            s.sendall(json.dumps(tosend).encode('utf-8'))
            s.close()
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"Error stopping robot: {e}")
            try:
                s.close()
            except:
                pass
        
        self.running=False

    def robot_forward(self, count):
        
        s=self.robot_connect()
        
        print(f"Starting forward movement for {count} seconds with obstacle detection...")
        # Start continuous forward movement
        tosend={"H": 22, "N": 3, "D1": 3, "D2": 50}
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        obstacle_detected = False
        
        def state_check(data):
            nonlocal obstacle_detected
            
            if data == "{Heartbeat}":
                # On each heartbeat, check for obstacles
                tosend={"H": 22, "N": 21, "D1": 1}
                s.sendall(json.dumps(tosend).encode('utf-8'))
            elif "true" in data:
                print("Obstacle detected during movement - stopping")
                obstacle_detected = True
                self.obstacle_stopped = True
                return False  # Stop the heartbeat loop
            elif "false" in data:
                # No obstacle, continue moving
                pass
                
            return True

        # Run for specified time or until obstacle detected
        self.robot_heatbeat(s, count, state_check)
        self.robot_all_stop(s)
    
        return not obstacle_detected



    def robot_backward(self, count):
        
        s=self.robot_connect()
        
        print(f"Starting backward movement for {count} seconds...")
        # Start continuous backward movement (D1: 4 = backward)
        tosend={"H": 22, "N": 3, "D1": 4, "D2": 50}
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        self.robot_heatbeat(s, count)
        self.robot_all_stop(s)
    
        return True

    def robot_rotate_left(self, count: int):
        
        s=self.robot_connect()
        
        print(f"Starting left rotation for {count} seconds...")
        
        tosend={"H": 22, "N": 3, "D1": 1, "D2": 50}
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        self.robot_heatbeat(s, count)
        self.robot_all_stop(s)
        
        return True
    
    
    def robot_rotate_right(self, count: int):
        
        s=self.robot_connect()
        
        print(f"Starting right rotation for {count} seconds...")
        
        tosend={"H": 22, "N": 3, "D1": 2, "D2": 50}
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        self.robot_heatbeat(s, count)
        self.robot_all_stop(s)
        
        return True

    def is_finished(self):

        return self.running == False
       

    
    def robot_detect_obstacle(self):
        """
        Check if an obstacle was detected during the last movement.
        This returns the cached flag set by movement commands.
        Assumes obstacles don't move between checks.
        """
        result = self.obstacle_stopped
        if result:
            print("Obstacle was detected during last movement")
            self.obstacle_stopped = False  # Reset flag after reading
        else:
            print("No obstacle detected during last movement")
        
        return result      
        
    
        
    def robot_camera_control(self, direction):
        """
        Control camera servo movement
        direction: 1=tilt_down, 2=tilt_up, 3=pan_right, 4=pan_left, 5=center
        """
        s = self.robot_connect()
        
        print(f"Moving camera: {['', 'tilt_down', 'tilt_up', 'pan_right', 'pan_left', 'center'][direction]}")
        tosend = {"H": 22, "N": 106, "D1": direction}
        
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        self.robot_heatbeat(s, 1)
        self.robot_all_stop(s)

    def robot_camera_pan_left(self, count):
        """Pan camera left multiple times"""
        for i in range(int(count)):
            self.robot_camera_control(3)
            time.sleep(0.1)
        
        # Check for obstacle after camera has moved
        s = self.robot_connect()
        tosend = {"H": 22, "N": 21, "D1": 1}
        s.sendall(json.dumps(tosend).encode('utf-8'))
        time.sleep(0.2)
        try:
            data = s.recv(1024).decode('utf-8')
            if "true" in data:
                self.obstacle_stopped = True
        except:
            pass
        self.robot_all_stop(s)

    def robot_camera_pan_right(self, count):
        """Pan camera right multiple times"""
        for i in range(int(count)):
            self.robot_camera_control(4)
            time.sleep(0.1)
        
        # Check for obstacle after camera has moved
        s = self.robot_connect()
        tosend = {"H": 22, "N": 21, "D1": 1}
        s.sendall(json.dumps(tosend).encode('utf-8'))
        time.sleep(0.2)
        try:
            data = s.recv(1024).decode('utf-8')
            if "true" in data:
                self.obstacle_stopped = True
        except:
            pass
        self.robot_all_stop(s)