import time
import socket
import json

class RobotControl():
    
    
    def __init__(self, robot_ip):
        self.robot_ip=robot_ip
        self.running=False
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
        
        while True:
            
            try:
            
                data = s.recv(1024)
                if data:
                    
                    data = data.decode("utf-8") 
                    print(data)
                    
                    if data == "{Heartbeat}":
                        print("Got Heartbeat, sending...")
                        s.sendall("{Heartbeat}".encode('utf-8'))


                    if callback!=None:
                        res=callback(data)
                        # if the callback fails, return false
                        if res==False:
                            # tell the caller that the count did not complete
                            count_complete=False
                            break;
                        
            except socket.timeout as e:
                pass
            
            # see if we detect anything on the sensors


        
            count=count-1
            
            if count<=0:
                break;

        return(count_complete)
            
    def robot_all_stop(self, s):
        
        tosend={ "N":100}
        
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        s.close()
        self.running=False

    def robot_forward(self, count):
        
        s=self.robot_connect()
        
        print("Sending command...")
        tosend={"H": 22, "N": 1, "D1": 0, "D2": 50, "D3": 1}
    
        s.sendall(json.dumps(tosend).encode('utf-8'))
    
        def state_check(data):
            # we get called on a heartbeat and also on the sensor state reply
            # so we need to only check the sensor state result
            return_val=True

            sensor_state=None
            if "true" in data:
                sensor_state=True
                # we have seen somthing, so return false meaning stop
                return_val=False
            elif "false" in data:
                sensor_state=False
            else:
                # ok, reply was not from the heartbeat, so reask sensor state
                # 1 : Check whether an obstacle is detected.            
                tosend={"H": 22, "N": 21, "D1": 1}
                s.sendall(json.dumps(tosend).encode('utf-8'))        

            return(return_val)

        final_res=True

        # if the heartbeat fails, its because the state_check returned false
        # this means that we detected somthing from the sensor            
        final_res = self.robot_heatbeat(s, count, state_check)

        self.robot_all_stop(s)
    
        return(final_res)



    def robot_rotate_left(self, count: int):
        
        s=self.robot_connect()
        
        print("Sending command...")
        
        # D1 = direction, 
        # 1=left, 2=right, 3=forward, 4=back
        # D3 = speed
        tosend={"H": 22, "N": 3, "D1": 1, "D2": 50}
    
        s.sendall(json.dumps(tosend).encode('utf-8'))
    
        self.robot_heatbeat(s, count)
        self.robot_all_stop(s)
    
    
    def robot_rotate_right(self, count: int):
        
        s=self.robot_connect()
        
        print("Sending command...")
        
        # D1 = direction, 
        # 1=left, 2=right, 3=forward, 4=back
        # D3 = speed
        tosend={"H": 22, "N": 3, "D1": 2, "D2": 50}
    
        s.sendall(json.dumps(tosend).encode('utf-8'))
    
        self.robot_heatbeat(s, count)
        self.robot_all_stop(s)

    def is_finished(self):

        return self.running == False
       

    
    def robot_detect_obstacle(self):
    
        current_state=False
        
        s=self.robot_connect()
        
        # 1 : Check whether an obstacle is detected.
        # 2 : Check the value of the ultrasonic sensor
        tosend={"H": 22, "N": 21, "D1": 1}
        
        s.sendall(json.dumps(tosend).encode('utf-8'))
        
        
        def state_check(data):
            nonlocal current_state
            print("In data: "+str(data))

            if "true" in data:
                current_state=True
            elif "false" in data:
                current_state=False                

            return(True)
            
        self.robot_heatbeat(s, 1, state_check) 
        self.robot_all_stop(s)        
        
        print("obstacle "+str(current_state))        
        
        return(current_state)      
        
    
        