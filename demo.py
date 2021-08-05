'''
Copyright (c) 2021 Out of the BOTS
MIT License (MIT) 
Author: Shane Gingell
'''

#Robotis MicroPython
from pycm import *
import time

#chnage namespace of const so not to conflict with pycm.const
from micropython import const as mp_const

#unable to get Phone class to inherit smart classes methods
#hopefully fixed in future CM-550 micropython upadtes
class Phone:
    
    def __init__(self):
        self.cam_end = mp_const(0)
        self.cam_rear = mp_const(1)
        self.cam_front = mp_const(2)
        self.cam_blank = mp_const(0)
        self.cam_face = mp_const(1)
        self.cam_colour = mp_const(2)
        self.cam_motion = mp_const(3)
        self.cam_line = mp_const(4)
   
    def set_cam(self, cam):
        smart.write8(10020, cam)
        
    def set_cam_zoom(self, magnifaction):
        smart.write8(magnifaction)
    
    def set_cam_fuction(self, function):
        smart.write8(10040, function)
 
    #volume in range 0 to 255       
    def set_volume(self, volume):
        smart.write8(10240, volume)

    #return x,y in a 5x5 grid and will return [0,0] if not detected        
    def get_face(self):
        position = smart.read8(10080)
        if position == 0 : return [0,0]
        if position % 5 ==0: return [5, position // 5 + 1]
        else: return [position % 5, position // 5 + 1]

    def get_touch(self):
        position = smart.read8(10310)
        if position == 0 : return (0,0)
        if position % 5 ==0: return (5, position // 5 + 1)
        else: return (position % 5, position // 5 + 1)
        
    #magnifaction 1-10 bigger, 11-20 smaller
    def pic_display(self, position, image_num, magnifaction):
        smart.write32(10140, ((position[0] - 1) * 5 + position[1]) | (image_num << 8) | (magnifaction << 16))
        
    def pic_clear_all(self):
        self.pic_display([1,0],0,0)
        
    def back_ground(self, image_num):
        smart.write8(10130, image_num)
        
    def speak(self, speach_num):
        smart.write8(10180, speach_num)
        
    def listen(self):
        smart.write8(10220, 1)
        
        #block till listening is finished
        time.sleep(1)
        while smart.read8(10220): time.sleep(0.1)
        
    def get_speach(self):
        return smart.read8(10230)
        
    def play_audio(self, audio_num):
        smart.write8(10200, audio_num)
        




class Dynamixel:
    
    def __init__(self, ID_num):
        self.dynamixel = DXL(ID_num)
        
    def torque_on(self, state):
        self.dynamixel.write8(64, state)
        
    def set_drive_mode(self, mode):
        self.dynamixel.write8(10, mode)
        
    def set_operating_mode(self, mode):
        self.dynamixel.write8(11, mode)
    
    def set_goal_velocity(self, velocity):
        self.dynamixel.write32(112, velocity)
        
    def set_goal(self, goal):
        self.dynamixel.write32(116, goal)

    def get_position(self):
        return self.dynamixel.read32(132)
 
    def dynamixel_wait(self):
        while (self.dynamixel.read8(123) & 1 )==0: time.sleep(0.1)
 

console(const.USB)

#init_pose
motion.play(1)

#create instance og Dynamixels needed for face tracking
dxl_waist = Dynamixel(11)
dxl_head_pitch = Dynamixel(9)


#set torque on
dxl_head_pitch.torque_on(True)
dxl_waist.torque_on(True)



#wait for smart phone connection
smart.wait_connected()

#create instance of Phone class
phone = Phone()

#setup screen, screen_orientation still needs to be added to Phone class
smart.display.screen_orientation(2) 
phone.pic_clear_all()
phone.set_volume(255)

#display Out of the BOTS logo
phone.back_ground(2)
time.sleep(3)

#goto second pose
motion.play(2)

#display start button and speak
phone.pic_display((3,3), 2, 3)
phone.speak(4)

#wait till start button is pressed
while phone.get_touch() != (3,3): time.sleep(0.1)
motion.play(3)

#clear start button
phone.pic_clear_all()

#display smiley face
phone.back_ground(3)

#set up face detection with front camera
phone.set_cam(phone.cam_front)
phone.set_cam_fuction(phone.cam_face)

#reset clap count
mic.clear()

#while loop tracks face
while True:
    
    face_pos = phone.get_face()

    if face_pos[0] != 0:
        dxl_waist.set_goal_velocity(abs(face_pos[0] - 3) * 20)
        dxl_waist.set_goal(dxl_waist.get_position() + (face_pos[0] - 3) * 100)
        dxl_head_pitch.set_goal_velocity(abs(face_pos[1] - 3) * 15)
        dxl_head_pitch.set_goal(dxl_head_pitch.get_position() - (face_pos[1] - 3) * 100)
        
    #exit if hear a clap
    if mic.counting(): break

#turn off camera    
phone.set_cam(phone.cam_end)


while True:
    
    #change pose
    motion.play(2)
    
    phone.speak(5)
    time.sleep(1.3)
    phone.listen()
    
    speach_result = phone.get_speach()
    
    #if play some beats heard
    if speach_result == 6:
        phone.play_audio(2)
        motion.play(4)
        motion.wait()
        phone.play_audio(0)
    
    #if shutdown heard   
    elif speach_result == 7: break

    #someone is speaking some shit
    else:
        phone.speak(8)
        time.sleep(1.3)

#display sad face, goto sad pose and play sad speach
phone.back_ground(4)
motion.play(5)
phone.speak(9)

time.sleep(4)


#clear screen and goto init pose
phone.back_ground(0)
motion.play(1)





  