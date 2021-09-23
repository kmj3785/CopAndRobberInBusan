import os, sys
sys.path.append(os.getcwd())
import torch
import torch.nn as nn
import pandas as pd
import sqlite3
import json
import seaborn as sn
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from rnn.rnn import RNN
from rnn.utils import path_to_tensor

engine = sqlite3.connect('./test/data/test_data.sqlite3')
node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
path_df = pd.read_sql('SELECT * FROM rob_paths', engine)
path_df['path'] = path_df['path'].apply(lambda x : json.loads(x)) # json to list

def test_data_split(paths):
    x_test = []
    y_test = []

    for path in paths:
        x_element = []
        for i in range(len(path)-1):
            x_element.append(path[:i+1])
        y_element = path[1:]
        x_test.extend(x_element)
        y_test.extend(y_element)

    y_test = [int(node_df.loc[[y], ['groupNum']].groupNum) for y in y_test] # nodeId to groupNum
    return x_test, y_test

def model_load(n_group, n_hidden, model_path):
    model = RNN(n_group, n_hidden, n_group)
    checkpoint = torch.load(model_path)
    model.load_state_dict(checkpoint['model'])

    return model

def predict(model, path):
    with torch.no_grad():
        path_one_hot_tensor, path_tensor = path_to_tensor(path)
        
        hidden = model.init_hidden()
        
        for i in range(path_one_hot_tensor.size()[0]):
            output, hidden = model(path_one_hot_tensor[i], hidden)
        
        group_idx = torch.argmax(output).item()
        return group_idx+1
        
if __name__ == '__main__':
    n_group = 34
    n_hidden = 8

    model_100 = model_load(n_group, n_hidden, './rnn/weights/100_100_100.tar')
    model_100.eval()

    model_500 = model_load(n_group, n_hidden, './rnn/weights/500_100_100.tar')
    model_500.eval()

    model_10000 = model_load(n_group, n_hidden, './rnn/weights/10000_100_100.tar')
    model_10000.eval()

    x_test, y_test = test_data_split(path_df.path)
    print('testing data split is completed')

    y_pred_100 = [predict(model_100, x) for x in x_test]
    print('model_100 testing is completed')
    y_pred_500 = [predict(model_500, x) for x in x_test]
    print('model_500 testing is completed')
    y_pred_10000 = [predict(model_10000, x) for x in x_test]
    print('model_10000 testing is completed')

    label = [x for x in range(1, n_group+1)]

    confusion_matrix_100 = confusion_matrix(y_test, y_pred_100, labels=label)
    confusion_matrix_500 = confusion_matrix(y_test, y_pred_500, labels=label)
    confusion_matrix_10000 = confusion_matrix(y_test, y_pred_10000, labels=label)

    plt.rcParams['figure.figsize'] = [16, 4]
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    sn.heatmap(confusion_matrix_100, square=True, ax=ax1)
    sn.heatmap(confusion_matrix_500, square=True, ax=ax2)
    sn.heatmap(confusion_matrix_10000, square=True, ax=ax3)
    plt.show()

    # report_dict_100 = classification_report(y_test, y_pred_100, output_dict=True)
    # report_dict_500 = classification_report(y_test, y_pred_500, output_dict=True)
    # report_dict_10000 = classification_report(y_test, y_pred_10000, output_dict=True)

    report_df_100 = pd.DataFrame(classification_report(y_test, y_pred_100, output_dict=True)).transpose()
    report_df_500 = pd.DataFrame(classification_report(y_test, y_pred_500, output_dict=True)).transpose()
    report_df_10000 = pd.DataFrame(classification_report(y_test, y_pred_10000, output_dict=True)).transpose()

    plt.figure()
    plt.plot(report_df_100[['f1-score']], 'r', label='data size : 100')
    plt.plot(report_df_500[['f1-score']], 'b', label='data size : 500')
    plt.plot(report_df_10000[['f1-score']], 'g', label='data size : 10000')
    plt.grid(True, axis='y')
    plt.title('F1-score of model per learning data size', fontsize=25)
    plt.xlabel('Group Number')
    plt.ylabel('F1-score')
    plt.legend()
    plt.show()