from flask import Flask, request, jsonify, render_template
from keras.preprocessing.image import img_to_array
#from keras.models import Sequential
from keras.models import load_model
from keras import backend as K
from flask_cors import CORS
#import tensorflow as tf
from PIL import Image
#import keras.models
import numpy as np
import base64
#import sys
import io
#import re 
import os

# Initiate Flask.
app = Flask(__name__)

cors = CORS(app, resource={r"/*":{"origins": "*"}})

def loadModel():
    global model
    
    # Load the trained model.
    model = load_model('models/Modelo_Duas_Classes_98.h5')
    
    return model

def processImage(image, expectedSize):
   '''
    Process the image inserted by the interface. Checks if the image is RGB, resizes it to the expected size and converts it to an array.
    INPUT
        IMAGE: Inserted image.
        EXPECTEDSIZE: Final size that the model expects.
    OUTPUT:
        Returns the processed image.
    '''
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(expectedSize)
    image = img_to_array(image)
    image = image.astype('float32') 
    image /= 255

    return image

loadModel()

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route("/information", methods=['GET', 'POST'])
def information():
    return render_template("informacoes.html")

# Makes a request to the prediction model.
@app.route('/predict', methods = ['GET','POST'])
def predict():
    '''
    Makes the prediction process for the inserted image.
    INPUT:
        MESSAGE: Recieves the Json from the request.
        ENCODEDIMAGE: Recieves the value associated with the key 'image' of Json alocated in the variable
        'message'. The value is the image recieved by the client side in base64 format. 
        DECODEDIMAGE: Makes a b64decode of the image.
        PROCESSEDIMAGE: Recieves an instance of PIL dependence to open an image wich is alocated in memory in base64 format and than, keep the image in a bytes format.
        PREDICTION: Recieves the predict method, passing the processed image in numpyArray and, calls the method 'tolist()' to convert it in a list.
    OUTPUT: 
        Dictionary which will be sent to the client side. Contains the keys responsible for prediction with the values that the model returns.
    '''
    message = request.get_json(force = True)
    encodedImage = message['image']
    decodedImage = base64.b64decode(encodedImage)
    image = Image.open(io.BytesIO(decodedImage))
    processedImage = processImage(image, expectedSize=(256, 239))
    
    prediction = model.predict(np.expand_dims(processedImage, axis = 0))

    # Class of the analyzed image.
    labelAnalyzedImage = model.predict_classes(np.expand_dims(processedImage, axis = 0)).tolist()
    
    # Predictions for the images classes.
    positivePrediction = (prediction[:,1] * 100).tolist() 
    negativePrediction = (prediction[:,0] * 100).tolist()

   # Sends the formatted response to the client side.
    response = {
        'predicao': {
            'sintomatica': positivePrediction,
            'assintomatica': negativePrediction,
            'classeImagem': labelAnalyzedImage
        }
    }
    
    return jsonify(response)

def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port)

if __name__ == '__main__':
    main()
