

import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'dataset'

# Check if the face module is available
if hasattr(cv2, 'face'):
    print("cv2.face module is available.")
else:
    print("cv2.face module is not available.")

try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("LBPH Face Recognizer created successfully.")
except AttributeError:
    print("cv2.face module is not available. Please ensure you have installed opencv-contrib-python.")
    
    
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

# function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = []
    # Duyệt đệ quy tất cả file trong các thư mục con
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                imagePaths.append(os.path.join(root, file))

    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        try:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        except Exception as e:
            print(f"[WARNING] Could not open {imagePath}: {e}")
            continue
        img_numpy = np.array(PIL_img, 'uint8')

        # Lấy id từ tên file: User.<id>.<count>.jpg
        try:
            id = int(os.path.split(imagePath)[-1].split(".")[1])
        except Exception as e:
            print(f"[WARNING] Could not parse id from {imagePath}: {e}")
            continue
        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y + h, x:x + w])
            ids.append(id)

    return faceSamples, ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

# Print the numer of faces trained and end program
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
