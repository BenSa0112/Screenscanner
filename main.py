from shutil import copyfile
from PIL import Image, ImageChops
import time
import cv2
import mss
import numpy as np
import json
from pathlib import Path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
import atexit
import os


def compare_img(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None


def exit_hook():
    text_file = open(path, "w")
    n = text_file.write("")
    text_file.close()
atexit.register(exit_hook)


def pytes(img):
    inverted_image = np.invert(img)
    new_text = pytesseract.image_to_string(inverted_image, lang="deu",config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
    text_file = open(path, "w")
    n = text_file.write(new_text)
    text_file.close()
    print(new_text)

#copyfile('settings.json','check\settings.json')
#os.startfile('check\check.exe')


file = Path("settings.json")
if file.exists():
    with open("settings.json", "r") as f:
        dict = json.load(f)
        monitor = dict["Monitor"]
        color1 = np.asarray([dict["Start_Colour"][0], dict["Start_Colour"][1], dict["Start_Colour"][2]])
        color2 = np.asarray([dict["End_Colour"][0], dict["End_Colour"][1], dict["End_Colour"][2]])
        path = dict["Path"]
        sample_file = Path(path)
        if not sample_file.exists():
            try:
                text_file = open(path, "w")
                n = text_file.write(' ')
                text_file.close()
            except:
                if not sample_file.exists():
                    print("Path does not exist.")
                    input("Check path ...")

else:
    print("Can´t find settings.json. Check if settings.json exists.")
    input("Check if settings.json is in root folder...")

while len(mss.mss().monitors)<=monitor:
    print("Monitor does not exist. Check selected Monitor.")
    input("Press enter to start again...")
    def clear(): os.system('cls')
    clear()

with mss.mss() as sct:
    while True:
#basis
        if len(sct.monitors)>monitor:
            screen = sct.monitors[monitor]
            img = np.asarray(sct.grab(screen))
        #read from Image
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mask = cv2.inRange(img_rgb, color1, color2)
#bbox
        # threshold
        thresh = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)[1]

        # get contours
        result = mask.copy()
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        i = 0
        list=[]
        content = ''
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
            list.append([x,y,content])
            roi = mask[y :y + h , x :x + w ]
            i += 1
        if i>0:
            # cut off one half
            half_height_loc = (i/2)-1
            height_cutoff = list[int(half_height_loc)][1]
            final_img = mask[:height_cutoff-50, :]
        else:
            final_img = mask
#pytes
        #check first if image has changed
        color_converted1 = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
        cmp_img1 = Image.fromarray(color_converted1)

        try:
            cmp_img2
        except NameError:
            color_converted2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cmp_img2 = Image.fromarray(color_converted2)

        if compare_img(cmp_img1,cmp_img2) is False:
            cmp_img2 = cmp_img1
            pytes(final_img)
        time.sleep(0.5)


