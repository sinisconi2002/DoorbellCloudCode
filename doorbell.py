#import collections
#from collections import abc
#collections.MutableMapping = abc.MutableMapping
from picamera import PiCamera
from rpi_lcd import LCD
from signal import pause
from time import sleep
from gpiozero import Button
import pyrebase
from datetime import datetime
import base64
import json

button = Button(17)
camera = PiCamera()
lcd = LCD()

config = {
	'apiKey': "AIzaSyASpod8P7JnGBYLDz6JO8Q2C3Dbss9YmBw",
	'authDomain': "smartdoorbellfinal.firebaseapp.com",
	'databaseURL': "https://smartdoorbellfinal-default-rtdb.firebaseio.com",
	'storageBucket': "smartdoorbellfinal.appspot.com"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()  
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("mosucalinracheta@gmail.com", "racheta")
today = datetime.now()
day_hour = today.strftime("%d-%m-%Y_%H-%M")
name = "img_" + day_hour
name_img = name + ".jpg"                               
db= firebase.database()
#data={"blacklist": "they are denied entry", "default": "everyone just goes in there",  "greenlist":"the Schengen of the doorbell"}
#.child("lists").set(data)

try:																																																																																																																																   
	#camera.start_preview()
	button.wait_for_press()
	#sleep(3)
	camera.capture(name_img)
	#camera.stop_preview()
	storage.child("DEFAULT/" + name_img).put(name_img)
	img_dict = {"person_name" : "person", "img_link": storage.child("DEFAULT/" + name_img).get_url(user["idToken"])}
	db.child("lists").child("default").update({name : img_dict})
	db.child("lists").child("latest").set(img_dict)
	sleep(30)
	toPrint = db.child("actions").get("print").val()
	access = db.child("actions").get("access").val()
	if(toPrint):
		if (access):
			lcd.text('Acceess granted!', 1)
		else:
			lcd.text('Acceess denied!', 1)
		sleep(5)	
		pause()
finally:
	print()
	lcd.clear()
