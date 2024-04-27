import cv2
import face_recognition
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from threading import Thread
import time

app = Flask(__name__)
user_database = {}
face_database = {}
usernames = []

def store_user_data(username, password):
    print("store user")
    user_database[username] = password
    
def check_available_username(username):
    print("check username")
    if username in usernames:
        return False
    return True


def store_face_data(username, face_encoding):
    print("store face")
    face_database[username] = face_encoding
    usernames.append(username)

def retrieve_face_data(username):
    print("retrieve")
    return face_database.get(username, None)

def facial_recognition_logic(image_data):
    print("face recog")
    camera = cv2.VideoCapture(0)
 
    counter = 0
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(list(face_database.values()), face_encoding)
            name = "Unknown"
            
            if True in matches:
                match_index = matches.index(True)
                camera.release()
                return usernames[match_index]
                
        counter += 1
        if counter > 500: 
            break
    camera.release()
    cv2.destroyAllWindows()
    return None
    
    
    face_locations = face_recognition.face_locations(image_data)
    face_encodings = face_recognition.face_encodings(image_data, face_locations)

    for username, stored_face_encoding in face_database.items():
        for face_encoding in face_encodings:
            match = face_recognition.compare_faces([stored_face_encoding], face_encoding)
            if True in match:
                # If a match is found, return the username
                match_index = match.index(True)
                return usernames[match_index]

    return None


@app.route('/capture_facial_data', methods=['POST'])
def capture_facial_data():
    print("capture")
    data = request.get_json()
    username = data.get('username')
    camera = cv2.VideoCapture(0)
    time.sleep(2)  
    counter = 0
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
	
		
        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]
            face_database[username] = face_encoding
            usernames.append(username)
            print("User " + str(username) + " added")
            camera.release()
            return
        
        counter += 1
        if counter > 80000:
            camera.release()
            return
    camera.release()
    return

def facial_scan_login():
    print("facial scan login")
    # Open camera and perform facial scan
    camera = WebcamVideoStream().start()
    face_location = None  
    
    while True:
        frame = camera.read()
        if frame is not None:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            if len(face_encodings) > 0:
                for username, stored_face_encoding in face_database.items():
                    matches = face_recognition.compare_faces([stored_face_encoding], face_encodings[0])
                    if True in matches:
                        camera.stop()
                        return redirect(url_for('account', username=username))
                face_location = face_locations[0]
        
        time.sleep(0.1)  
    return face_location



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('facial_scan'):
            matched_username = facial_recognition_logic(request)
            if matched_username:
                return redirect(url_for('account', username=matched_username))
                
        if request.form.get('register_button'):
            return redirect(url_for('register'))

    return render_template('index.html', username=request.args.get('username'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    print("reg")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in user_database:
            return jsonify({'error': 'Username already exists.'}), 400
        
        store_user_data(username, password)
        return redirect(url_for('account', username=username))
            
    return render_template('register.html')

@app.route('/account/<username>')
def account(username):
    return render_template('account.html', username=username)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
