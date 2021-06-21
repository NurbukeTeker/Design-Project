#!/usr/bin/python
# -*- coding: <encoding name> -*-
import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
import numpy as np

from PIL import Image
import pytesseract
import argparse
import cv2
import os
import os  # first you need to import the module 'os'
os.chdir('/home/nurbuke/Masaüstü/OttomanImageLabelingWebApp/tesseract-flask-image-labeling-master')
import mail_ottoman

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])
IMAGE_SIZE = (224, 224)
UPLOAD_FOLDER = 'uploads'

import logging
logger = logging.getLogger('api')

from ImageClass import Imageclass
global current_image
current_image = Imageclass("")
counter = current_image.counter

def resetImage():
    write_to_file()
    current_image = Imageclass("")
    counter = current_image.counter
    current_image.counter = counter+1
    return 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def write_to_file():

    import ntpath
    crop_name = ntpath.basename(current_image.name)
    f = open("sendMail/{}.txt".format(crop_name),"a" ,encoding='utf-8')
    output = str( current_image.newlabel)
    f.write(str(output))
    f.write("\n")
    f.close()
    return 

def check_text(line):
    characters = ["x","w","0","1","2","3","4","5","6","7","8","9","\\","\/"]
    for char in characters:
        if char  in  line:
            # print(char)
            return False     
    return True


def predictionImageOttoman(image):
    image = cv2.resize(image, None, fx=0.3, fy=0.3)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, 11)
#    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#    gray = cv2.medianBlur(gray, 3)
    config = "--psm 3"
    import ntpath
    crop_name = ntpath.basename(current_image.name)
    filename = "sendMail/{}.tif".format(crop_name)
    cv2.imwrite(filename, adaptive_threshold)
    
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'
    text = pytesseract.image_to_string(Image.open(filename),lang='ara',config=config)
    text = text.split("\n")
    # print("text:  ",text)

    output = []
    for  i in text:
        if (i != '') and (i != '\x0c')  :
            i = str(i)
            # print(i)


            output.append(i)
            
#    text = ''.join(output)
#    print(text)
#    return str(text)
    
    return output


def predict(file):
    image = cv2.imread(file)
    # print(image)    
    prediction = predictionImageOttoman(image)
    output =  prediction

    return output

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/handle_data', methods=['POST'])
def handle_data():
    print("hereeeeNOWWw")
    print(request.form)
    paragraph_text = request.form['saisie']
    print("paragraph_text",paragraph_text)
    current_image.newLabel(paragraph_text)
    resetImage()
    return redirect(url_for('template_test'))

#    return render_template("home.html", label=current_image.prediction, imagesource=current_image.name)



@app.route('/approve', methods=['POST'])
def approve():
    if "approve" in request.form:
          current_image.approved = True
          current_image.newlabel = current_image.prediction
          print("Onay verildi")
          print(current_image.name,current_image.approved )
    resetImage()
    return redirect(url_for('template_test'))
#    return render_template("home.html",  label=current_image.prediction, imagesource=current_image.name)


@app.route('/mailme', methods=['POST'])
def mailme():
    if "mailme" in request.form:
        mail_ottoman.sendMail()
    return redirect(url_for('template_test'))
#    return render_template("home.html",  label=current_image.prediction, imagesource=current_image.name)
    
@app.route("/")
def template_test():
    # resetImage()
    return render_template('home.html', label='', imagesource='file://null')


@app.route('/', methods=['POST'])
def upload_file():
    # print("HERREEE")
    if request.method == 'POST':
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            current_image.nameImage(file_path,counter)
            output = predict(file_path)
            current_image.labelImage(output)
            print(current_image.name,current_image.prediction )
            
            if  ' ' in output :
                output.remove(' ')
                if output == []:
                    output.append("Bulunamadı")
            if output == []:
                    output.append("Bulunamadı")
            print("OUTPUT:",output)
            # output = "\n".join(output)
            # output.replace('\n', '<br>')
            # print("NEWOUTPUT:",output)
            # output = "<p> " + output +"</p> "
    return render_template("home.html", label=output, imagesource=file_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.run(host = '127.0.0.1', port= '5009',debug=True, threaded=False)
#    app.run(host = '192.168.1.38', port= '5000')