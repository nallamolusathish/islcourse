# -*- coding: utf-8 -*-
"""hubconf.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EcytcUQflmUo0gLUXFEz-mFwJmXE3fza
"""

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, ToPILImage
from PIL import Image

transform_tensor_to_pil = ToPILImage()
transform_pil_to_tensor = ToTensor()

"""# Evaluation will load different dataset or different subsets

## Student list

## Any data set may be loaded
"""

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, ToPILImage
from PIL import Image
from torch.autograd import Variable
import matplotlib.pyplot as plt

def load_data():

    # Download training data from open datasets.
    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=ToTensor(),
    )

    # Download test data from open datasets.
    test_data = datasets.FashionMNIST(
        root="data",
        train=False,
        download=True,
        transform=ToTensor(),
    )
    
    return training_data, test_data

"""## sizes may be modified"""

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class ModifiedDataset(nn.Module):
  def __init__(self,given_dataset,shrink_percent=10):
    self.given_dataset = given_dataset
    self.shrink_percent = shrink_percent
    
  def __len__(self):
    return len(self.given_dataset)

  def __getitem__(self,idx):
    img, lab = self.given_dataset[idx]

    # print (type(img))
    # print (img.shape)

    img2 = transform_tensor_to_pil(img.squeeze())

    # print (img2.size)
    
    new_w = int(img2.size[0]*(1-self.shrink_percent/100.0))
    new_h = int(img2.size[1]*(1-self.shrink_percent/100.0))

    # print (new_w, new_h)

    img3 = img2.resize((new_w,new_h))

    # print (img3.size)

    x = transform_pil_to_tensor(img3)

    # print (x.shape)

    return x,lab

training_data, test_data = load_data()
mod_train_data = ModifiedDataset(training_data)
mod_test_data = ModifiedDataset(test_data)

print (training_data[0][0].shape)
#print (mod_train_data[0][0].shape)

def create_dataloaders(training_data, test_data, batch_size=64):

    # Create data loaders.
    train_dataloader = DataLoader(training_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)

    for X, y in test_dataloader:
        print(f"Shape of X [N, C, H, W]: {X.shape}")
        print(f"Shape of y: {y.shape} {y.dtype}")
        break
        
    return train_dataloader, test_dataloader

train_dataloader, test_dataloader=create_dataloaders(training_data, test_data)

def output_label(label):
    output_mapping = {
                 0: "T-shirt/Top",
                 1: "Trouser",
                 2: "Pullover",
                 3: "Dress",
                 4: "Coat", 
                 5: "Sandal", 
                 6: "Shirt",
                 7: "Sneaker",
                 8: "Bag",
                 9: "Ankle Boot"
                 }
    input = (label.item() if type(label) == torch.Tensor else label)
    return output_mapping[input]

a = next(iter(train_dataloader))
a[0].size()

kernel_size=3
padding=1
in_channels=1
out_channels=32

class FashionCNN(nn.Module):
    
    def __init__(self):
        super(FashionCNN, self).__init__()
        
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, padding=padding),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        
        self.layer2 = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        self.fc1 = nn.Linear(in_features=64*6*6, out_features=600)
        self.drop = nn.Dropout2d(0.25)
        self.fc2 = nn.Linear(in_features=600, out_features=120)
        self.fc3 = nn.Linear(in_features=120, out_features=10)
        
    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.view(out.size(0), -1)
        out = self.fc1(out)
        out = self.drop(out)
        out = self.fc2(out)
        out = self.fc3(out)
        
        return out

model = FashionCNN()
model.to(device)

error = nn.CrossEntropyLoss()

learning_rate = 0.001
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
print(model)

"""Training the model"""

num_epochs = 2
count = 0

# Lists for visualization of loss and accuracy 
loss_list = []
iteration_list = []
accuracy_list = []

# Lists for knowing classwise accuracy
predictions_list = []
labels_list = []

for epoch in range(num_epochs):
    for images, labels in train_dataloader:
        # Transfering images and labels to GPU if available
        images, labels = images.to(device), labels.to(device)
    
        train = Variable(images.view(64, 1, 28, 28))
        labels = Variable(labels)
        
        # Forward pass 
        outputs = model(train)
        loss = error(outputs,labels)
        
        # Initializing a gradient as 0 so there is no mixing of gradient among the batches
        optimizer.zero_grad()
        
        #Propagating the error backward
        loss.backward()
        
        # Optimizing the parameters
        optimizer.step()


        count+=1
        if (count % 10==0):
          print("epoch: {}, Loss: {}".format(epoch+1, loss.data))

    
        count += 1

if not (count % 50):    # It's same as "if count % 50 == 0"
      total = 0
      correct = 0
  
      for images, labels in test_dataloader:
          images, labels = images.to(device), labels.to(device)
          labels_list.append(labels)
      
          test = Variable(images.view(100, 1, 28, 28))
      
          outputs = model(test)
      
          predictions = torch.max(outputs, 1)[1].to(device)
          predictions_list.append(predictions)
          correct += (predictions == labels).sum()
      
          total += len(labels)
      
      accuracy = correct * 100 / total
      loss_list.append(loss.data)
      iteration_list.append(count)
      accuracy_list.append(accuracy)
        
      if not (count % 500):
          print("Iteration: {}, Loss: {}, Accuracy: {}%".format(count, loss.data, accuracy))

"""# Sample code invocation"""

'''examplerollnum = 'ykalidas'

examplerepo = examplerollnum + 'iittp/islcourse:midsem'

entrypoints = torch.hub.list(examplerepo,force_reload=True)

print (entrypoints)

train_data_loader1 = None

# model = torch.hub.load(examplerepo,'get_model',train_data=train_data,n_epochs=5, force_reload=True)
config1 = [(1,10,(3,3),1,'same'), (10,3,(5,5),1,'same'), (3,1,(7,7),1,'same')]
model = torch.hub.load(examplerepo,'get_model_advanced',train_data_loader=train_data_loader1,n_epochs=10, lr=1e-4,config=config1, force_reload=True)

print (model)

test_data_loader1 = None

a,p,r,f1 = torch.hub.load(examplerepo,'test_model',model1=model,test_data_loader=test_data_loader1,force_reload=True)

print (a,p,r,f1)'''