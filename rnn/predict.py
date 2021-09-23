import os, sys
sys.path.append(os.getcwd())

from rnn.rnn import RNN
from rnn.utils import path_to_tensor
import torch
import torch.nn as nn
import copy

'''
It allows the learning model to be applied to the project.
@author KMY
@version 1.0
'''

n_group = 34
n_hidden = 8
model = RNN(n_group, n_hidden, n_group)

checkpoint_test = torch.load('./rnn/weights/' + '10000_100_100.tar')
model.load_state_dict(checkpoint_test['model'])
model.eval()

model_state = copy.deepcopy(model.state_dict())


# input: the path nodeID of the rob, return: the group to which the rob moves to the next turn
def predict(path):
    with torch.no_grad():
        path_one_hot_tensor, path_tensor = path_to_tensor(path)
        
        hidden = model.init_hidden()
        
        for i in range(path_one_hot_tensor.size()[0]):
            output, hidden = model(path_one_hot_tensor[i], hidden)
        
        group_idx = torch.argmax(output).item()
        return group_idx+1

if __name__ == '__main__':
    x_predict = [1400016300, 1400016500, 1400016900, 1400016800, 1400005000, 1400005100, 1400005200, 1400020000, 1400005200, 1400020000, 1400005200, 1400020000, 1400005200, 1400020000]
    print(predict(x_predict))