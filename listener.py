import pyrebase
import shutil
import os
import urllib.request
import face_recognition
import time
import collections 
import firebase_admin
from firebase_admin import db, storage, messaging

blacklist_names = []
default_names = []
greenlist_names = []

blacklist_encodings = []
default_encodings = []
greenlist_encodings = []

tokens = ["ebfOdrALTI6ipYlHE37W9J:APA91bHcSd2-kN_vLJfKoHQ_hqiU_fXOqbUsF6hIHWJ1hFnQuNTJnMlJeQdGeFeOS0_EqZZd9WWe3Cks2KGOb-9W8uXNlyA6JpCY2R4iAjlZNqADVeZHNv4N8S6JQGJrprZaXIwiZvBk"]

#Here begins the logic of the API

def sendPush(title, msg, registration_token, dataObject):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg
        ),
        data=dataObject,
        tokens=registration_token
    )

    # Send a message to the device corresponding to the provided registration token.
    response = messaging.send_multicast(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)

#method for creating and initialising the folders and lists
def create_directories():
    os.mkdir(os.path.join(os.getcwd(), "blacklist"))
    os.mkdir(os.path.join(os.getcwd(), "default"))
    os.mkdir(os.path.join(os.getcwd(), "greenlist"))
    os.mkdir(os.path.join(os.getcwd(), "latest"))

def delete_directories():
    shutil.rmtree(os.path.join(os.getcwd(), "blacklist"))
    shutil.rmtree(os.path.join(os.getcwd(), "default")) 
    shutil.rmtree(os.path.join(os.getcwd(), "greenlist")) 
    shutil.rmtree(os.path.join(os.getcwd(), "latest")) 

config = {
	'apiKey': "AIzaSyASpod8P7JnGBYLDz6JO8Q2C3Dbss9YmBw",
	'authDomain': "smartdoorbellfinal.firebaseapp.com",
	'databaseURL': "https://smartdoorbellfinal-default-rtdb.firebaseio.com",
	'storageBucket': "smartdoorbellfinal.appspot.com"
}

#initialize the connection the firebase project using a try-catch
try:
    #create the directories for the images
    create_directories()

    #Create and connect to the firebase app using pyrebase
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password("mosucalinracheta@gmail.com", "racheta")
    db2 = firebase.database()

    #Create and connect to the firebase app using firebase_admin
    cred = firebase_admin.credentials.Certificate(os.path.join(os.getcwd(), 'key2.json'))
    default_app = firebase_admin.initialize_app(cred, config)
    bucket = storage.bucket()
    bucket_list = bucket.list_blobs(prefix="DEFAULT/")
    bucket_list_len = len(list(bucket_list))

    def create_blacklist():
            children = db2.child("lists").child("blacklist").get().val()
            
            if type(children) == collections.OrderedDict:
                for key, child in children.items():
                    img_name = key + ".jpg"
                    if img_name not in os.listdir("blacklist"):
                        urllib.request.urlretrieve(child["img_link"], os.path.join(os.getcwd(), "blacklist", img_name))
                        try:
                            image_to_encode = face_recognition.load_image_file(os.path.join(os.getcwd(), "blacklist", img_name))
                            image_encoding = face_recognition.face_encodings(image_to_encode)[0]
                            blacklist_encodings.append(image_encoding)
                            blacklist_names.append(child["person_name"])
                        except: 
                            pass                            

    def create_default():
            children = db2.child("lists").child("default").get().val()
            if type(children) == collections.OrderedDict:
                for key, child in children.items():
                    img_name = key + ".jpg"
                    if img_name not in os.listdir("default"):
                        urllib.request.urlretrieve(child["img_link"], os.path.join(os.getcwd(), "default", img_name))
                        try:
                            image_to_encode = face_recognition.load_image_file(os.path.join(os.getcwd(), "default", img_name))
                            image_encoding = face_recognition.face_encodings(image_to_encode)[0]
                            default_encodings.append(image_encoding)
                            default_names.append(child["person_name"])
                        except: 
                            pass                       
    
    def create_greenlist():
        children = db2.child("lists").child("greenlist").get().val()
        if type(children) == collections.OrderedDict:
            for key, child in children.items():
                img_name = key + ".jpg"
                if img_name not in os.listdir("greenlist"):
                    urllib.request.urlretrieve(child["img_link"], os.path.join(os.getcwd(), "greenlist", img_name))
                    try:
                        image_to_encode = face_recognition.load_image_file(os.path.join(os.getcwd(), "greenlist", img_name))
                        image_encoding = face_recognition.face_encodings(image_to_encode)[0]
                        greenlist_encodings.append(image_encoding)
                        greenlist_names.append(child["person_name"])
                    except:
                        pass
    
    create_blacklist()
    create_default()
    create_greenlist()
    
    #the loop which is the 'listener' for when an 
    while True:
        #print("Baszd meg")
        bucket_list = bucket.list_blobs(prefix="DEFAULT/")
        new_bucket_list_len = len(list(bucket_list))
        if new_bucket_list_len > bucket_list_len:
            #retrieve the latest image from the db
            latest = db.reference('/lists/latest').get()
            if os.path.exists(os.path.join(os.getcwd(), "latest", "latest.jpg")):
                os.remove(os.path.join(os.getcwd(), "latest", "latest.jpg"))
            urllib.request.urlretrieve(latest["img_link"], os.path.join(os.getcwd(), "latest", "latest.jpg"))    

            try:        
                #try to retreive the faces from the image in order to perform the face recognition      
                unknown_image = face_recognition.load_image_file(os.path.join(os.getcwd(), "greenlist", "latest.jpg"))
                face_locations = face_recognition.face_locations(unknown_image)
                face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
                #update the lists in order to make sure they are at the newest version
                create_blacklist()
                create_default()
                create_greenlist()
                
                #if at least a person is in the blacKlist, ACCES DENIED
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(blacklist_encodings, face_encoding)
                    name = "Unknown person"
                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = blacklist_names[first_match_index]
                        sendPush("A new visitor", f"{name} was at the front door! Access instantly denied", tokens, {'title': "A new visitor", 'message': f"{name} was at the front door! Access instantly denied", 'label': 'blacklist'})
                        break

                    #if at least a person is in the default list, you may approve or deny access
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(default_encodings, face_encoding)

                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        #first_match_index = matches.index(True)
                        name = default_names[first_match_index]
                        sendPush("A new visitor", f"{name} is at the front door!", tokens, {'title': "A new visitor", 'message': f"{name} is at the front door!", 'label': 'default'})
                        break

                    #if at least a person is in the green list, ACCESS GRANTED
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(greenlist_encodings, face_encoding)

                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = greenlist_names[first_match_index]
                        sendPush("A new visitor", f"{name} was at the front door! Access instantly granted", tokens, {'title': "A new visitor", 'message': f"{name} was at the front door! Access instantly granted", 'label': 'greenlist'})
                        break

            except:
                sendPush("A new visitor", 'Unknown person is at the front door!', tokens, {'title': "A new visitor", 'message': 'Unknown person is at the front door!', 'label': 'default'})
                
        bucket_list_len = new_bucket_list_len
        
finally:
    delete_directories()