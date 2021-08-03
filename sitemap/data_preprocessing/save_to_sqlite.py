import pandas as pd
import json
import sqlite3

# read data from .csv file
node_df = pd.read_csv('./sitemap/data_preprocessing/data/geumjeong_node_information.csv', encoding='euc-kr') # node 데이터
edge_df = pd.read_csv('./sitemap/data_preprocessing/data/geumjeong_edge_information.csv', encoding='euc-kr') # edge 데이터

# rename column
node_df['linkedNode'] = ''
node_df.columns = ['nodeId', 'nodeType', 'korName', 'latitude', 'longitude', 'linkedNode']
edge_df.columns = ['edgeId', 'fnodeId', 'enodeId', 'korName', 'roadLength']

# add linked node data to node_df
fnode_id_set = set(edge_df['fnodeId'].values)
for id in fnode_id_set:
    enode_id_set = set(edge_df[edge_df['fnodeId']==id]['enodeId'].values)
    enode_id_json = json.dumps(list([int(x) for x in enode_id_set]))
    node_df.loc[node_df.nodeId==id, 'linkedNode'] = enode_id_json

# save to database
engine = sqlite3.connect("./db.sqlite3")
node_df.to_sql(name='node_information', con=engine, if_exists='append', index=False)
edge_df.to_sql(name='edge_information', con=engine, if_exists='append', index=False)