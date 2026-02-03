############################################# IMPORTING ################################################
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2, os, csv, time, datetime, threading, pickle
import numpy as np
import pandas as pd
from PIL import Image
import pyttsx3
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import gdown

############################################# CNN MODEL SETUP ################################################

FACENET_MODEL_PATH = "facenet_keras.h5"
_facenet_model = None
registered_faces = {}  # {serial: (name, embedding)}

def download_facenet_model():
    """
    Downloads facenet_keras.h5 if not present.
    """
    url = "https://drive.google.com/uc?id=1NVR5jP4YZaOgvciKy5rIDr-7kK5x5i-n"  # public facenet_keras.h5
    if not os.path.isfile(FACENET_MODEL_PATH):
        print("Downloading facenet_keras.h5 (~90MB)...")
        gdown.download(url, FACENET_MODEL_PATH, quiet=False)
        print("Download complete: facenet_keras.h5")

def load_facenet_model():
    global _facenet_model
    if _facenet_model is None:
        if not os.path.isfile(FACENET_MODEL_PATH):
            download_facenet_model()
        _facenet_model = load_model(FACENET_MODEL_PATH)
    return _facenet_model

def preprocess_face(img, required_size=(160,160)):
    img = cv2.resize(img, required_size)
    img = img.astype('float32')
    mean, std = img.mean(), img.std()
    img = (img - mean) / (std + 1e-6)
    return np.expand_dims(img, axis=0)

def get_embedding(model, face_pixels):
    return model.predict(face_pixels)[0]

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

############################################# HELPERS ################################################

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def tick():
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200, tick)

def contact():
    mess._show(title='Contact us', message="Please contact us on : 'your_email@gmail.com' ")

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if not exists:
        mess._show(title='Missing File', message='Please add haarcascade_frontalface_default.xml')
        window.destroy()

# VOICE
def speak_text(text):
    def _speak(t):
        try:
            engine = pyttsx3.init()
            engine.say(t)
            engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
    threading.Thread(target=_speak, args=(text,)).start()

spoken_ids = set()

############################################# REGISTRATION ################################################

def TakeImages():
    check_haarcascadefile()
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    serial = 0
    exists = os.path.isfile("StudentDetails/StudentDetails.csv")
    if exists:
        with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for _ in reader1:
                serial += 1
        serial = (serial // 2)
    else:
        with open("StudentDetails/StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
        serial = 1
    Id = txt.get()
    name = txt2.get()
    if name.isalpha() or ' ' in name:
        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        sampleNum = 0
        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                sampleNum += 1
                cv2.imwrite("TrainingImage/"+name+"."+str(serial)+"."+Id+'.'+str(sampleNum)+".jpg", img[y:y+h,x:x+w])
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                cv2.imshow('Taking Images', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 30:
                break
        cam.release()
        cv2.destroyAllWindows()
        row = [serial,'',Id,'',name]
        with open('StudentDetails/StudentDetails.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        message1.configure(text="Images Taken for ID : "+Id)
    else:
        message.configure(text="Enter Correct Name")

############################################# TRAIN IMAGES ################################################

def TrainImages():
    assure_path_exists("TrainingImageLabel/")
    model = load_facenet_model()
    global registered_faces
    registered_faces = {}

    df = pd.read_csv("StudentDetails/StudentDetails.csv")
    for idx,row in df.iterrows():
        serial = int(row['SERIAL NO.'])
        name = row['NAME']
        Id = row['ID']
        # get one image per person for embedding
        img_path = None
        for f in os.listdir("TrainingImage/"):
            if f.split(".")[1] == str(serial):
                img_path = os.path.join("TrainingImage/", f)
                break
        if img_path is not None:
            img = cv2.imread(img_path)
            face_pixels = preprocess_face(img)
            embedding = get_embedding(model, face_pixels)
            registered_faces[serial] = (name, embedding)

    # 🔹 Save registered_faces permanently
    with open("TrainingImageLabel/embeddings.pkl", "wb") as f:
        pickle.dump(registered_faces, f)

    message1.configure(text="Profiles Saved Successfully")

############################################# TRACKING ################################################

def TrackImages():
    check_haarcascadefile()
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")

    global registered_faces
    # 🔹 Load saved embeddings
    if os.path.exists("TrainingImageLabel/embeddings.pkl"):
        with open("TrainingImageLabel/embeddings.pkl", "rb") as f:
            registered_faces = pickle.load(f)
    else:
        mess._show("Error", "No trained profiles found. Please save profile first.")
        return

    for k in tv.get_children():
        tv.delete(k)

    cam = cv2.VideoCapture(0)
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    model = load_facenet_model()
    df = pd.read_csv("StudentDetails/StudentDetails.csv")
    col_names = ['Id','','Name','','Date','','Time']

    global spoken_ids
    spoken_ids = set()
    speak_text("Starting attendance. Please look at the camera.")

    while True:
        ret,im = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,1.2,5)
        for(x,y,w,h) in faces:
            face = im[y:y+h,x:x+w]
            face_pixels = preprocess_face(face)
            embedding = get_embedding(model, face_pixels)

            identity = "Unknown"
            best_score = -1
            best_name = None
            best_serial = None
            for serial,(name,db_emb) in registered_faces.items():
                sim = cosine_similarity(embedding, db_emb)
                if sim > best_score:
                    best_score = sim
                    best_name = name
                    best_serial = serial
            if best_score > 0.5:  # threshold
                identity = best_name
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                Id = df.loc[df['SERIAL NO.']==best_serial]['ID'].values[0]
                attendance = [str(Id),'',identity,'',date,'',timeStamp]
                csv_path = "Attendance/Attendance_"+date+".csv"
                exists = os.path.isfile(csv_path)
                with open(csv_path,'a+') as f:
                    writer = csv.writer(f)
                    if not exists:
                        writer.writerow(col_names)
                    writer.writerow(attendance)
                # add to GUI
                tv.insert('',0,text=Id,values=(identity,date,timeStamp))
                if best_serial not in spoken_ids:
                    spoken_ids.add(best_serial)
                    speak_text("Welcome " + identity)
            cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(im,identity,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,255,255),2)
        cv2.imshow("Taking Attendance", im)
        if cv2.waitKey(1)==ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()

######################################## GUI FRONT-END ###########################################

window = tk.Tk()
window.geometry("1280x720")
window.title("Attendance System")
window.configure(background='#2d420a')

frame1 = tk.Frame(window,bg="#c79cff")
frame1.place(relx=0.11,rely=0.17,relwidth=0.39,relheight=0.80)

frame2 = tk.Frame(window,bg="#c79cff")
frame2.place(relx=0.51,rely=0.17,relwidth=0.38,relheight=0.80)

message3 = tk.Label(window,text="CNN Face Recognition Attendance System",fg="white",bg="#2d420a",width=55,height=1,font=('comic',29,'bold'))
message3.place(x=10,y=10)

datef = tk.Label(window,text=time.strftime("%d-%B-%Y"),fg="#ff61e5",bg="#2d420a",width=55,height=1,font=('comic',22,'bold'))
datef.place(x=350,y=70)

clock = tk.Label(window,fg="#ff61e5",bg="#2d420a",width=55,height=1,font=('comic',22,'bold'))
clock.place(x=750,y=70)
tick()

head2 = tk.Label(frame2,text="For New Registrations",fg="black",bg="#00fcca",font=('comic',17,'bold'))
head2.grid(row=0,column=0)

head1 = tk.Label(frame1,text="Attendance",fg="black",bg="#00fcca",font=('comic',17,'bold'))
head1.place(x=0,y=0)

lbl = tk.Label(frame2,text="Enter ID",width=20,fg="black",bg="#c79cff",font=('comic',17,'bold'))
lbl.place(x=80,y=55)
txt = tk.Entry(frame2,width=32,fg="black",font=('comic',15,'bold'))
txt.place(x=30,y=88)

lbl2 = tk.Label(frame2,text="Enter Name",width=20,fg="black",bg="#c79cff",font=('comic',17,'bold'))
lbl2.place(x=80,y=140)
txt2 = tk.Entry(frame2,width=32,fg="black",font=('comic',15,'bold'))
txt2.place(x=30,y=173)

message1 = tk.Label(frame2,text="1)Take Images  >>>  2)Save Profile",bg="#c79cff",fg="black",width=39,height=1,font=('comic',15,'bold'))
message1.place(x=7,y=230)

message = tk.Label(frame2,text="",bg="#c79cff",fg="black",width=39,height=1,font=('comic',16,'bold'))
message.place(x=7,y=450)

tv=ttk.Treeview(frame1,height=13,columns=('name','date','time'))
tv.column('#0',width=82)
tv.column('name',width=130)
tv.column('date',width=133)
tv.column('time',width=133)
tv.grid(row=2,column=0,padx=(0,0),pady=(50,0),columnspan=4)
tv.heading('#0',text='ID')
tv.heading('name',text='NAME')
tv.heading('date',text='DATE')
tv.heading('time',text='TIME')

clearButton = tk.Button(frame2,text="Take Images",command=TakeImages,fg="white",bg="#6d00fc",width=34,height=1,font=('comic',15,'bold'))
clearButton.place(x=30,y=300)

trainImg = tk.Button(frame2,text="Save Profile",command=TrainImages,fg="white",bg="#6d00fc",width=34,height=1,font=('comic',15,'bold'))
trainImg.place(x=30,y=380)

trackImg = tk.Button(frame1,text="Take Attendance",command=TrackImages,fg="black",bg="#3ffc00",width=35,height=1,font=('comic',15,'bold'))
trackImg.place(x=30,y=50)

quitWindow = tk.Button(frame1,text="Quit",command=window.destroy,fg="black",bg="#eb4600",width=35,height=1,font=('comic',15,'bold'))
quitWindow.place(x=30,y=450)

window.mainloop()
