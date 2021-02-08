import cv2
import numpy as np
import djitellopy as tello
import time
import KeyPressModule as kp
kp.init()

fbRange = [6200, 6800]
pid = [0.4, 0.4, 0]
w, h = 360, 240
pError = 0

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



def findFace(img):
    faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListC = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]


def trackFace(me, info, w, pid, pError):
    area = info[1]
    fb = 0
    x, y = info[0]
    error = x - w // 2  # How far away is the center of image

    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))

    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20
    if x == 0:
        speed = 0
        error = 0

    me.send_rc_control(0, fb, 0, speed)
    return error


while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    try:
        ret, img = tello_video.read()
        if ret:
            img = cv2.resize(img, (w, h))
            img, info = findFace(img)
            trackFace(me, info, w, pid, pError)
            cv2.imshow("Tello", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as err:
        tello_video.release()
        cv2.destroyAllWindows()
        print(err)
