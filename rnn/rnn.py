import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt 
from utils import create_path_tensor

class RNN(nn.Module):
    # implement RNN from scratch rather than using nn.RNN
    def __init__(self, input_size, hidden_size, output_size):
        super(RNN, self).__init__()
        
        self.hidden_size = hidden_size
        self.i2h = nn.Linear(input_size + hidden_size, hidden_size)
        self.i2o = nn.Linear(input_size + hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)
        
    def forward(self, input_tensor, hidden_tensor):
        combined = torch.cat((input_tensor, hidden_tensor), 1)
        
        hidden = self.i2h(combined)
        output = self.i2o(combined)
        output = self.softmax(output)
        return output, hidden
    
    def init_hidden(self):
        return torch.zeros(1, self.hidden_size)

n_group = 34

n_hidden = 64
rnn = RNN(n_group, n_hidden, n_group)

criterion = nn.NLLLoss()
learning_rate = 0.005
optimizer = torch.optim.SGD(rnn.parameters(), lr=learning_rate)

def train(path_one_hot_tensor, path_tensor):
    hidden = rnn.init_hidden()

    loss = 0

    for i in range(path_one_hot_tensor.size()[0]):
        output, hidden = rnn(path_one_hot_tensor[i], hidden)
        if i < path_one_hot_tensor.size()[0]-1:

            loss += criterion(output, path_tensor[i+1])

    loss /= path_one_hot_tensor.size()[0]

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return output, loss.item()

current_loss = 0
all_losses = []
plot_steps, print_steps = 10, 50
epoch = 1000

for i in range(epoch):
    path_tensor_generator = create_path_tensor()
    print(i)

    for path_one_hot_tensor, path_tensor in path_tensor_generator:

        output, loss = train(path_one_hot_tensor, path_tensor)
        current_loss += loss 
    
    if (i+1) % plot_steps == 0:
        all_losses.append(current_loss / plot_steps)
        current_loss = 0
        
    if (i+1) % print_steps == 0:
        print(i)
        #guess = group_from_output(output)
        #correct = "CORRECT" if guess == path_tensor else f"WRONG ({path_tensor})"
        #print(f"{i+1} {(i+1)/epoch*100} {loss:.4f} {line} / {guess} {correct}")
        
plt.figure()
plt.plot(all_losses)
plt.show()
plt.savefig(f'lossresult/SGD_{epoch}_{n_hidden}.png', dpi = 3000)