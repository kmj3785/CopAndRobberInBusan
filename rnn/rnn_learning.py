import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt 
from utils import create_path_tensor
from rnn import RNN
import time

'''
Based on the path of the robber stored in the database, 
predict the group to which the robber will move next and store the learning model.
@author KMJ, KMY
@version 1.2, Add a code to save the learning model.
'''

if __name__ == '__main__':
    n_group = 34

    n_hidden = 8
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
    plot_steps, print_steps = 1, 10
    epoch = 50

    for i in range(epoch):
        start_time = time.time()

        path_tensor_generator = create_path_tensor()

        for path_one_hot_tensor, path_tensor in path_tensor_generator:

            output, loss = train(path_one_hot_tensor, path_tensor)
            current_loss += loss 
        
        if (i+1) % plot_steps == 0:
            all_losses.append(current_loss / plot_steps)
            current_loss = 0
            
        # checkpoint
        if (i+1) % print_steps == 0:
            torch.save({
                'epoch': i+1,
                'all_losses': all_losses,
                'model': rnn.state_dict(),
                'optimizer': optimizer.state_dict()
            }, f'./rnn/weights/all_{i+1:0>3}.tar')
            print(f'{i+1}th learning model is saved.')
        
        end_time = time.time()-start_time
        print(f'epoch: {i+1}\tlearning time: {end_time}s')
            
    plt.figure()
    plt.plot(all_losses)
    plt.show()
    plt.savefig(f'loss_result/SGD_{epoch}_{n_hidden}.png', dpi = 3000)