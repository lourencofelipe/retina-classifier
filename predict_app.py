from flask import Flask, request, jsonify, render_template
import keras.models
from keras.preprocessing.image import img_to_array
from keras.models import Sequential
from keras.models import load_model
from keras import backend as K
from flask_cors import CORS
import tensorflow as tf
from PIL import Image
import numpy as np
import base64
import sys
import io
import re 
import os

# Inicia o app flask.
app = Flask(__name__)

cors = CORS(app, resource={r"/*":{"origins": "*"}})

def carregarModelo():
    global model
    #model = tf.keras.models.load_model('models/Classificacao_RD_Duas_Categorias_03.h5')
    # Carrega o arquivo do modelo treinado.
    model = load_model('models/Modelo_Duas_Classes_98.h5')
    
    return model

def processarImagem(imagem, tamanhoEsperado):
    '''
        Processa imagem inserida por meio da interface. Verifica se a imagem está em RGB, 
        redimensiona a imagem para o tamanho esperado e convete imagem para array.
    INPUT
        IMAGEM: Imagem inserida.
        TAMANHOESPERADO: Tamanho final que o modelo espera.
    OUTPUT   
        Retorna imagem processada.
    '''
    if imagem.mode != "RGB":
        imagem = imagem.convert("RGB")
    imagem = imagem.resize(tamanhoEsperado)
    imagem = img_to_array(imagem)
    imagem = imagem.astype('float32') 
    imagem /= 255

    return imagem

carregarModelo()

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route("/informations", methods=['GET', 'POST'])
def informacoes():
    return render_template("informacoes.html")

# Criação de endpoint que requisita o modelo para predição.
@app.route('/predict', methods = ['GET','POST'])
def predict():
    '''
        Realiza o processo de predição para a imagem inserida.
    INPUT
        MESSAGE: Recebe o json da requisição. 
        IMAGEMCODIFICADA: Recebe o valor associado a chave 'image' do JSON alocado na variável 'message'. 
        O valor é a imagem recebida via client no formato base64.
        IMAGEMDECODIFICADA: Decodifica a imagem incialmente da base64
        IMAGEM: Recebe instância da dependência PIL para abrir uma imagem que está em memória na base64 e então
        manter com formato em bytes.
        IMAGEMPROCESSADA: Recebe a imagem processada no tamanho utilizado pelo modelo.
        PREDICAO: Recebe o método predict, recebendo a imagem processada em numpyArray, então deve-se instanciar
        método tolist() para converter em uma lista;
        RESPONSE: Dicionário que será enviado de volta para o client. Contém as chaves responsáveis pela predição 
        com os valores retornados pelo modelo.
    OUTPUT   
        Retorna json da resposta.
    '''
    message = request.get_json(force = True)
    imagemCodificada = message['image']
    imagemDecodificada = base64.b64decode(imagemCodificada)
    imagem = Image.open(io.BytesIO(imagemDecodificada))
    imagemProcessada = processarImagem(imagem, tamanhoEsperado=(256, 239))
    
    predicao = model.predict(np.expand_dims(imagemProcessada, axis = 0))

    # Classe da imagem analisada.
    rotuloImagemAnalisada = model.predict_classes(np.expand_dims(imagemProcessada, axis = 0)).tolist()
    
    # Predições para as classes de imagens.
    predicaoPositiva = (predicao[:,1] * 100).tolist() 
    predicaoNegativa = (predicao[:,0] * 100).tolist()

   # Envia a resposta em json para o client.
    response = {
        'predicao': {
            'sintomatica': predicaoPositiva,
            'assintomatica': predicaoNegativa,
            'classeImagem': rotuloImagemAnalisada
        }
    }
    
    return jsonify(response)

def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port)

if __name__ == '__main__':
    main()
