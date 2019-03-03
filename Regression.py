import math
import torch.optim as optim
from BayesBackpropagation import *
import matplotlib.pyplot as plt
plt.switch_backend('agg')

# Define training step for regression
def train(net, optimizer, data, target, NUM_BATCHES):
    #net.train()
    for i in range(NUM_BATCHES):
        net.zero_grad()
        x = data[i].reshape((-1, 1))
        y = target[i].reshape((-1,1))
        loss = net.BBB_loss(x, y)
        loss.backward()
        optimizer.step()

#Hyperparameter setting
TRAIN_EPOCHS = 500
SAMPLES = 10
TEST_SAMPLES = 10
BATCH_SIZE = 200
NUM_BATCHES = 20
TEST_BATCH_SIZE = 100
CLASSES = 1
PI = 0.5
SIGMA_1 = torch.FloatTensor([math.exp(-0)]).to(DEVICE)
SIGMA_2 = torch.FloatTensor([math.exp(-6)]).to(DEVICE)

print('Generating Data set.')

#Data Generation step
if torch.cuda.is_available():
    Var = lambda x, dtype=torch.cuda.FloatTensor: Variable(torch.from_numpy(x).type(dtype)) #converting data to tensor
else:
    Var = lambda x, dtype=torch.FloatTensor: Variable(torch.from_numpy(x).type(dtype)) #converting data to tensor

x = np.random.uniform(-0.1, 0.6, size=(NUM_BATCHES,BATCH_SIZE))
noise = np.random.normal(0, 0.02, size=(NUM_BATCHES,BATCH_SIZE)) #metric as mentioned in the paper
y = x + 0.3*np.sin(2*np.pi*(x+noise)) + 0.3*np.sin(4*np.pi*(x+noise)) + noise
X = Var(x)
Y = Var(y)

x_test = np.linspace(-0.3, 1,TEST_BATCH_SIZE)
y_test = x_test + 0.3*np.sin(2*np.pi*x_test) + 0.3*np.sin(4*np.pi*x_test)
X_test = Var(x_test)

#plt.scatter(x, y, c='navy', label='target')
#plt.legend()
#plt.tight_layout()
#plt.show()
#print(x.shape)

#Training
print('Training Begins!')

#Declare Network
net = BayesianNetwork(inputSize = 1,\
                      CLASSES = CLASSES, \
                      layers=np.array([100,100]), \
                      activations = np.array(['relu','relu','none']), \
                      SAMPLES = SAMPLES, \
                      BATCH_SIZE = BATCH_SIZE,\
                      NUM_BATCHES = NUM_BATCHES,\
                      hasScalarMixturePrior = True,\
                      PI = PI,\
                      SIGMA_1 = SIGMA_1,\
                      SIGMA_2 = SIGMA_2).to(DEVICE)

#Declare the optimizer
#optimizer = optim.SGD(net.parameters(),lr=1e-4,momentum=0.9) #
optimizer = optim.Adam(net.parameters())

for epoch in range(TRAIN_EPOCHS):
    print('Epoch: ', epoch + 1)
    train(net, optimizer,data=X,target=Y,NUM_BATCHES=NUM_BATCHES)

print('Training Ends!')

#Testing
outputs = torch.zeros(TEST_SAMPLES+1, TEST_BATCH_SIZE, CLASSES).to(DEVICE)
for i in range(TEST_SAMPLES):
    outputs[i] = net.forward(X_test)
outputs[TEST_SAMPLES] = net.forward(X_test)
pred_mean = outputs.mean(0).data.cpu().numpy().squeeze(1) #Compute mean prediction
pred_std = outputs.std(0).data.cpu().numpy().squeeze(1) #Compute standard deviation of prediction for each data point

#Visualization
plt.scatter(x, y,marker='x', c='navy', label='target')
plt.plot(x_test, pred_mean, c='royalblue', label='Prediction')
plt.fill_between(x_test, pred_mean - 3 * pred_std, pred_mean + 3 * pred_std,
                     color='cornflowerblue', alpha=.5, label='+/- 3 std')
plt.plot(x_test, y_test, c='grey', label='truth')
plt.legend()
plt.tight_layout()
plt.savefig('./Results/Regression.png')
#plt.show()

#Save the trained model
#torch.save(net.state_dict(), './Models/Regression.pth')