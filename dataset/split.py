import pandas as pd
from sklearn.model_selection import train_test_split

test_path = 'test.csv'
dev_path = 'validation.csv'
train_path = 'train.csv'

labelled = pd.read_csv('labelled.csv')
autolabelled = pd.read_csv('autolabelled.csv')

labelled = labelled.loc[(labelled['object_tree'] != '[]')]
autolabelled = autolabelled.loc[(autolabelled['object_tree'] != '[]')]
autolabelled['json_tree'] = '{}'

autolabelled=autolabelled.sample(frac=0.25, random_state=1)

data = pd.concat([labelled, autolabelled])

train, test = train_test_split(data, test_size=0.2,train_size=0.8, random_state=1, shuffle=True)
train, valid = train_test_split(train, test_size=0.125,random_state=1, shuffle=True)

train.to_csv(train_path)
test.to_csv(test_path)
valid.to_csv(dev_path)
