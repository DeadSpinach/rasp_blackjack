import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import ImageFont, ImageTk
import PIL
from tkinter import *
import proc
import sqlite3


class Sampleranks:
    def __init__(self):
        self.img = []
        self.name = "Placeholder"

class Samplesuits:
    def __init__(self):
        self.img = []
        self.name = "Placeholder"

def doall():
    
    global rtop, stop, rbot, sbot

    im = cv2.imread('cards1a.jpg')
    (h, w) = im.shape[:2]
    imtop = im[0:int(h/2), 0:w]
    imbot = im[int(h/2):h, 0:w]
    
    rtop, stop = lookforit(imtop)
    rbot, sbot = lookforit(imbot)
    
def countit(cardname):
    ranks = ['Ace','Two','Three','Four','Five','Six','Seven',
                 'Eight','Nine','Ten','Jack','Queen','King']
    for i in range(len(ranks)):
        if cardname == ranks[i]:
            if i > 9:
                i = 9
            return i+1
    return 0


def charthelp(psum, dsum):
    if psum < 9:
        return "You should hit!"
    if psum == 9:
        if dsum < 3 or dsum > 6:
            return "You should hit!"
        else:
            return "DOUBLE DOWN!"
    if psum == 10:
        if dsum > 9:
            return "You should hit!"
        else:
            return "DOUBLE DOWN!"
    if psum == 11:
        return "DOUBLE DOWN!"
    if psum == 12:
        if dsum < 4:
            return "You should hit!"
    if psum > 11 and psum < 17:
        if dsum > 6:
            return "You should hit!"
    else:
        return "Better stand this one"


def dbadd(rs, ss):
    dum = 0
    mh = 0
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS BLACKJACK (rank text, suit text, hand int)''')
    c.execute("SELECT COUNT(*) FROM BLACKJACK")
    for row in c:
        if row[0] == 0:
            for i in range(len(rs)):
                c.execute("INSERT INTO BLACKJACK VALUES (?, ?, ?)", (rs[i], ss[i], 1))
        else:
            c.execute("SELECT rank, suit, MAX(hand) FROM BLACKJACK GROUP BY hand")
            for row in c:
                mh = row[2]
                for i in range(len(rs)):
                    if rs[i] == row[0] and ss[i] == row[1]:
                        dum = 1
                        rs[i] == "dummy"
            if dum != 1:
                mh = mh + 1
            for i in range(len(rs)):
                if rs[i] != "dummy":
                    c.execute("INSERT INTO BLACKJACK VALUES (?,?,?)", (rs[i], ss[i], mh))
    #conn.commit()
    #conn.close()

def cvalue():
    cval = 0
    c = conn.cursor()
    c.execute("SELECT rank FROM BLACKJACK")
    for row in c:
        if row[0] in ['Two','Three','Four','Five','Six']:
            cval = cval + 1
        if row[0] in ['Ten','Jack','Queen','King', 'Ace']:
            cval = cval - 1
    return cval

def purgedb():
    c = conn.cursor()
    c.execute("DROP TABLE BLACKJACK")


def lookforit(im):

    tranks = []
    tsuits = []
    i=0
    best_diff = 2000
    for Rank in ['Ace','Two','Three','Four','Five','Six','Seven',
                 'Eight','Nine','Ten','Jack','Queen','King']:
        tranks.append(Sampleranks())
        tranks[i].name = Rank
        file = str(i+1) + '.jpg'
        tranks[i].img = cv2.imread('ranks/'+file, cv2.IMREAD_GRAYSCALE)
        #cv2.imshow('kck',tranks[i].img)
        i = i + 1
    i=0
    for Suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
        tsuits.append(Samplesuits())
        tsuits[i].name = Suit
        file = 's' + str(i+1) + '.jpg'
        tsuits[i].img = cv2.imread('ranks/'+file, cv2.IMREAD_GRAYSCALE)
        #cv2.imshow('kck',tsuits[i].img)
        i = i + 1


    
    #cv2.imshow('kck',im)
    imthresh = proc.pproc(im)
    
    contours, cardlist = proc.finder(imthresh)
    cards = []
    #print(cardlist)
    for i in range(len(contours)):
        if (cardlist[i] == 1):
            cards.append(contours[i])

    listranks = []
    listsuits = []
    
    for i in range(len(cards)):
        cnt = cards[i]
        per = cv2.arcLength(cnt,True)
        epsilon = per/100
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        pts = np.float32(approx)
        x,y,width,height = cv2.boundingRect(cnt)
        avg = np.sum(pts, axis=0)/4
        centr = [int(avg[0][0]),int(avg[0][1])]
        print(centr)
        cimage = proc.cutout(im, pts, width, height)
        #if i==1: cv2.imshow('kck', cimage)


        corner = cimage[0:84,0:24]
        corner = cv2.resize(corner, (0,0), fx=4, fy=4)
        white_level = corner[15,int((24*4)/2)]
        thresh_level = white_level - 30
        if (thresh_level <= 0):
            thresh_level = 1
        retval, cornthresh = cv2.threshold(corner, thresh_level, 255,cv2. THRESH_BINARY_INV)
        #if i==2: cv2.imshow('kck', cornthresh)
        rank = cornthresh[0:180,0:96]
        suit = cornthresh[181:336, 0:96]
        rank = proc.resize_rs(rank,125,70)
        suit = proc.resize_rs(suit,100,70)
        
        #print(best_diff)

        best_name = ""
        best_suit = ""
        for item in tranks:
            diff = cv2.absdiff(rank, item.img)
            rank_diff = int(np.sum(diff)/255)
            if rank_diff < best_diff:
                best_diff = rank_diff
                best_name = item.name
        if best_name != "":
            listranks.append(best_name)
        #print(best_diff)
        #print(best_name)
        best_diff = 2000
        for item in tsuits:
            diff = cv2.absdiff(suit, item.img)
            rank_diff = int(np.sum(diff)/255)
            if rank_diff < best_diff:
                best_diff = rank_diff
                best_suit = item.name
        if best_suit != "":
            listsuits.append(best_suit)
        #print(best_diff)
        #print(best_suit)
        best_diff = 2000
    print(listranks)
    print(listsuits)
    #    cv2.putText(im, (best_name + ' of '),
    #                (centr[0]-80, centr[1]-10),5,1,(255,0,0))
    #    cv2.putText(im, (best_suit),
    #                (centr[0]-30, centr[1]+10),5,1,(255,0,0))
    #cv2.drawContours(im,cards, -1, (255,0,0), 2)
    #cv2.imshow('kck', im)
    return(listranks, listsuits)

if __name__ == '__main__':

    conn = sqlite3.connect('blackjack.db')
    purgedb()
    doall()
    window = Tk()
    window.title("Blackjack helper")
    window.geometry("800x600")
    btn = Button(window, text="Update", command=doall)
    btn.config(height="2", width="20")
    btn.place(x="220", y="550")
    btn2 = Button(window, text="Shuffle", command=purgedb)
    btn2.config(height="2", width="20")
    btn2.place(x="380", y="550")
    size = 100, 125
    w0 = 100
    psumcards = 0
    aces = 0
    for i in range(len(rbot)):
        if rbot[i] == "Ace":
            aces = aces +1
        else:
            psumcards = psumcards + countit(rbot[i])
        load = PIL.Image.open("gr/" + rbot[i] + sbot[i] + ".png")
        load.thumbnail(size, PIL.Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(window, image=render)
        img.image = render
        img.place(x=w0,y=370)
        w0 = w0 + 150
    if aces > 0:
        for j in range(aces):
            if psumcards + 11 > 21:
                psumcards = psumcards + 1
            else:
                psumcards = psumcards + 11
    bottext = Label(window, text=("Player's cards value: " + str(psumcards)))
    bottext.config(font=("Courier", 14), bg="darkblue", fg="white")
    bottext.place(x=100, y=340)
    w0 = 100
    dsumcards = 0
    aces = 0
    for i in range(len(rtop)):
        for i in range(len(rtop)):
            if rtop[i] == "Ace":
                aces = aces +1
            else:
                dsumcards = dsumcards + countit(rtop[i])
        load = PIL.Image.open("gr/" + rtop[i] + stop[i] + ".png")
        load.thumbnail(size, PIL.Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(window, image=render)
        img.image = render
        img.place(x=w0,y=50)
        w0 = w0 + 150
    if aces > 0:
        for j in range(aces):
            if dsumcards + 11 > 21:
                dsumcards = dsumcards + 1
            else:
                dsumcards = dsumcards + 11
    rs = rtop + rbot
    ss = stop + sbot
    dbadd(rs, ss)
    cval = 0
    cval = cvalue()
    print(cval)
    ctext = Label(window, text=("CC: " + str(cval)))
    ctext.config(font=("Courier", 14), bg="darkgreen", fg="white")
    ctext.place(x=700, y=50)
    bottext = Label(window, text=("Dealer's cards value: " + str(dsumcards)))
    bottext.config(font=("Courier", 14), bg="darkblue", fg="white")
    bottext.place(x=100, y=180)
    verd = charthelp(psumcards, dsumcards)
    v = Label(window, text=verd)
    v.config(font=("Courier", 24), bg="darkred", fg="white")
    v.place(x=250, y=260)
    window.configure(background="darkblue")
    
    window.mainloop()


    
    
    
