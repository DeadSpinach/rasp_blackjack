import numpy as np
import cv2

CARD_MIN_AREA = 20000


def pproc(im):


    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    imblur = cv2.GaussianBlur(imgray,(5,5),0)
    
    img_w, img_h = np.shape(im)[:2]
    threshlvl = 120 + (imgray[int(img_h/100)][int(img_w/2)]/3)
    ret, imthresh = cv2.threshold(imblur,threshlvl,255,cv2.THRESH_BINARY)

    return imthresh




def finder(im):
    contours, hierarchy = cv2.findContours(im,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cardlist = np.zeros(len(contours),dtype=int)
    for i in range(len(contours)):
        size = cv2.contourArea(contours[i])
        per = cv2.arcLength(contours[i],True)
        epsilon = per/100
        #print(size)
        approx = cv2.approxPolyDP(contours[i],epsilon,True)
        if ((size > CARD_MIN_AREA) and
            (hierarchy[0][i][3] == -1) and (len(approx) == 4)):
            cardlist[i] = 1
    return contours, cardlist


def cutout(image, pts, width, height):

    #ukladanie rogow prostokata opinajacego karte w odpowiedniej kolejnosci
    rect = np.zeros((4, 2), dtype = "float32")
    w = 200
    h = 300
    s = np.sum(pts, axis = 2)
    
    #sortowanie wierzcholkow (tl - top left itd.)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    #wykrycie czy karta jest poziomo czy pionowo
    if width < height:
        rect[0] = tl
        rect[1] = tr
        rect[2] = br
        rect[3] = bl

    if width > height:
        rect[0] = bl
        rect[1] = tl
        rect[2] = tr
        rect[3] = br

    dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0, h-1]], np.float32)
    M = cv2.getPerspectiveTransform(rect,dst)
    warp = cv2.warpPerspective(image, M, (w, h))
    warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
    #cv2.imshow('kck',warp)
    return warp


def resize_rs(rs, w, h):
    rs_cnts, hier = cv2.findContours(rs, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    rs_cnts = sorted(rs_cnts, key=cv2.contourArea,reverse=True)
    if len(rs_cnts) != 0:
        x1,y1,w1,h1 = cv2.boundingRect(rs_cnts[0])
        rs_roi = rs[y1:y1+h1, x1:x1+w1]
        rs_sized = cv2.resize(rs_roi, (h,w), 0, 0)
        return rs_sized
    else:
        print('NOT FOUND')
        return 0
