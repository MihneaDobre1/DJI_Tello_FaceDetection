from djitellopy import tello
import cv2
import KeyPressModule as kp

import time

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
tello_video = cv2.VideoCapture('udp://@0.0.0.0:11111')
me.streamon()

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 40
    if kp.getKey("LEFT"):
        lr = -speed
    elif kp.getKey("RIGHT"):
        lr = speed
    if kp.getKey("UP"):
        fb = speed
    elif kp.getKey("DOWN"):
        fb = -speed
    if kp.getKey("w"):
        ud = speed
    elif kp.getKey("s"):
        ud = -speed
    if kp.getKey("a"):
        yv = speed
    elif kp.getKey("d"):
        yv = -speed

    if kp.getKey("l"):
        me.land(); time.sleep(3)
    if kp.getKey("k"):
        me.takeoff()
    # if kp.getKey("z"):
    #     cv2.imwrite(f"Resources/Images/{time.time()}.jpg", img)
    #     time.sleep(0.3)

    return [lr,fb,ud,yv]



while True:

    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1],vals[2], vals[3])
    try:
        ret, frame = tello_video.read()
        if ret:

            cv2.imshow("Tello",frame)

            cv2.waitKey(1)
    except Exception as err:
        tello_video.release()
        cv2.destroyAllWindows()
        print(err)


