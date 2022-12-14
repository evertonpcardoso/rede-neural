# -*- coding: utf-8 -*-
"""Rede-neural.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DAJdzjt4pne7nUYXOin_kSuF0i_asZLn
"""

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
import torchvision
from time import time
from torchvision import datasets, transforms
from torch import nn, optim

transform = transforms.ToTensor()

trainset = datasets.MNIST('./MNIST_data/', download=True, train=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)

valset = datasets.MNIST('./MNIST_data/', download=True, train=False, transform=transform)
valloader= torch.utils.data.DataLoader(valset, batch_size=64, shuffle=True)

dataiter = iter(trainloader)
imagens, etiquetas = dataiter.next()
plt.imshow(imagens[0].numpy().squeeze(), cmap='gray_r');

print(imagens[0].shape)#para verificar as dimensões do tensor de cada imagem
print(etiquetas[0]. shape)#para verificar as dimensões do tensor de cada etiqueta

torch.Size([1, 28, 28])
torch.Size([])

class Modelo(nn.Module):
  def __init__(self):
    super(Modelo, self).__init__()
    self.linear1 = nn.Linear(28*28, 128)# Camada de entrada, 784 neurônios que se ligam a 128
    self.linear2 = nn.Linear(128, 64)#Camda interna 2, 64 neurônios que se ligam a 64
    self.linear3 = nn.Linear(64, 10)# Camada interna 2, 64 neurônios que se ligam a 19
    # Para a camada de saída não e necessário definir nada pois só precisamos pegar o output da camada interna 2

  def forward(self, X):
    X = F.relu(self.linear1) #Função de ativação da camada de entrada para a camada interna 1
    X = F.relu(self.linear2)# Função de ativação da camada interna 1 para a camada interna 2
    X - self.linear3(X) # Função de ativação da camada interna 2 para a camada de saída, nesse caso f(x) = x
    return F.log_softmax(X, dim=1) # Dados utilizados para calcular a perda

def treino(modelo, trainloader, device):

  otimizador = optim.SGD(modelo.parameters(), lr=0.01, momentum=0.5)# Define a politica de atualização dos pesos e da bias
  inicio = time() #Rimer para sabermos quanto tempo levou o treino

  criterio = nn.NLLLoss() #Definindo o criterio para calcular a perda
  EPOCHS = 10 # Numer de epochs que o algoritmo redará
  modelo.train() # Ativando o modo de treinamento do modelo

  for epoch in range(EPOCHS):
    perda_acumulada = 0 #inicialização da perda acumulada da epoch em questão

    for imagens, etiquetas in trainloader:

      imagens = imagens.view(imagens.shape[0], -1)# convertendo as imagens para "vetores" de 28*28 casas para ficarem compativeis com a 
      otimizador.zero_grad() #zerando os gradientes por conta do ciclo anterior

      output = modelo(imagens.to(device)) #colocando os dados no modelo
      perda_instantanea = criterio(output, etiquetas.to(device))#calculando a perda da epoch em questão

      perda_instantanea.backward() #back propagation a partir da perda

      otimizador.step()#atualizando os pesos e a bias

      perda_acumulada += perda_instantanea.item()#atualização da perda acumulada

    else: 
      print("Epoch {} - Perda resultante: {}".format(epoch+1, perda_acumulada/len(trainloader)))

  print("\nTempo de treino (em minutos) =",(time()-inicio)/60)

def validacao(modelo, valloader, device):
    conta_corretas, conta_todas = 0, 0
    for imagens, etiquetas in valloader:
      for i in range(len(etiquetas)):
        img = imagens[i].view(1, 784)
        #desativar o autograd para acelar a validação. Grafos computacionais dinâmicos tem um custo alto de processamento
        with torch.no_grad():
            logps = modelo(img.to(device))# output do modelo em escala logaritmica


        ps = torch.exp(logps)#converte output para escala normal(lembrando que é um tensor)
        probab = list(ps.cpu().numpy()[0])
        etiqueta_pred = probab.index(max(probab))#converte o tensor em um numero, no caso, o numero que o modelo previu como correto
        etiqueta_certa = etiquetas.numpy()[i]
        if(etiqueta_certa == etiqueta_pred):#compara a previsão com o valor correto
          conta_corretas += 1
        conta_todas += 1


    print("Total de imagens testadas=", conta_todas)
    print("\nPrecisão do modelo= {}%".format(conta_corretas*100/conta_todas))

modelo = Modelo()#inicializa o modelo

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #modelo rodará na GPU se possível
modelo.to(device)