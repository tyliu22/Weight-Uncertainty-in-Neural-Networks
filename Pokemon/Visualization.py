import math
import sys
sys.path.append('../')
from BayesBackpropagation import *
import numpy as np
import copy
import matplotlib.pyplot as plt
import json
from matplotlib import colors
import pandas as pd
import colorsys
plt.switch_backend('agg')

def loadPokemonModel(filename):
    # Hyperparameter declaration
    BATCH_SIZE = 20
    TEST_BATCH_SIZE = 1000
    CLASSES = 18
    TRAIN_EPOCHS = 1000
    SAMPLES = 20
    PI = 0.5
    SIGMA_1 = torch.FloatTensor([math.exp(-0)])
    SIGMA_2 = torch.FloatTensor([math.exp(-6)])
    if torch.cuda.is_available():
        SIGMA_1 = torch.cuda.FloatTensor([math.exp(-0)])
        SIGMA_2 = torch.cuda.FloatTensor([math.exp(-6)])
    INPUT_SIZE = 3

    LAYERS = np.array([200,200,200])
    NUM_BATCHES = 0
    ACTIVATION_FUNCTIONS = np.array(['relu','relu','relu','softmax'])
    net = BayesianNetwork(inputSize = INPUT_SIZE,\
                            CLASSES = CLASSES, \
                            layers=np.array([200,200,200]), \
                            activations = np.array(['relu','relu','relu','softmax']), \
                            SAMPLES = SAMPLES, \
                            BATCH_SIZE = BATCH_SIZE,\
                            NUM_BATCHES = NUM_BATCHES,\
                            hasScalarMixturePrior = True,\
                            PI = PI,\
                            SIGMA_1 = SIGMA_1,\
                            SIGMA_2 = SIGMA_2).to(DEVICE)

    net.load_state_dict(torch.load(filename, map_location='cpu'))
    net.eval()
    return net

def loadPokemonTypeMap():
    with open('PokemonTypeMap.json') as f:
        pokemonType = json.load(f)
    for x in range(18):
        pokemonType[x] = pokemonType.pop(str(x))
    return pokemonType

def test(net, r,g,b, pokemonType, TEST_SAMPLES):
    temp = torch.tensor(np.asarray([r,g,b]).astype(np.float32)).to(DEVICE)
    result = []
    for i in range(TEST_SAMPLES):
        output = net.forward(temp)
        a = output[0].data.cpu().numpy()
        result.append(np.exp(a) / (np.exp(a)).sum())
        
    mean = np.mean(result, axis = 0)
    std = np.std(result, axis = 0)
    result = pd.DataFrame({'Mean.Probability': mean,'Std':std})
    result['Type'] = result.index.values.astype(np.int)
    result = result.replace({'Type': pokemonType})
    result = result.sort_values(by='Mean.Probability', ascending=False)
    result = result.iloc[0]
    return result
    
net = loadPokemonModel('./Model.pth')
pokemonType = loadPokemonTypeMap()

#Initialize the HSV values
H = np.arange(0, 1.01, 0.01)
S = 1
V = 1

labels = [] #To store Pokemon's type
col = [] #To store Pokemon's colour in RGB
variance = [] #To store standard deviation for a colour

TEST_SAMPLES= 10

for h in H:
    r,g,b= colorsys.hsv_to_rgb(h, S, V) #convert hsv to rgb
    col.append((r,g,b))
    temp = test(net,r,g,b,pokemonType,TEST_SAMPLES)
    labels.append(temp['Type'])
    variance.append("{0:.4f}".format(temp['Std']))
sizes = np.ones(len(labels)) #Set equal weights to every color in pie chat
r = pd.DataFrame({'Type':labels,'Weight':sizes,'Colour':col,'Hue':H,'Std':variance})
r = r.sort_values(by=['Hue'], ascending=False) #To form the spectrum
r = r.drop(['Hue'],axis=1)
r = r.drop_duplicates()

#Type classification graph
patches, texts = plt.pie(r['Weight'], colors=r['Colour'], startangle=90,labels=r['Type'],rotatelabels=True)
plt.axis('equal')
plt.savefig('./Type.png')

#Standard deviation fluctuation graph
plt.figure(2)
patches, texts = plt.pie(r['Weight'], colors=r['Colour'], startangle=90,labels=r['Std'],rotatelabels=True)
plt.axis('equal')
plt.savefig('./Standard deviation.png')
