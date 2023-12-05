import pandas as pd
from sklearn.model_selection import train_test_split
import os


data_dir = "dataset" + os.path.sep


test_path = data_dir + "test.csv"
dev_path = data_dir + "validation.csv"
train_path = data_dir + "train.csv"

labelled = pd.read_csv(data_dir + "labelled.csv")
autolabelled = pd.read_csv(data_dir + "autolabelled.csv")

labelled = labelled.loc[(labelled["object_tree"] != "[]")]
autolabelled = autolabelled.loc[(autolabelled["object_tree"] != "[]")]
autolabelled["json_tree"] = "{}"

autolabelled = autolabelled.sample(frac=0.15, random_state=1)

data = pd.concat([labelled, autolabelled])

train, test = train_test_split(data, test_size=0.35, random_state=1, shuffle=True)
train, valid = train_test_split(train, test_size=0.15, random_state=1, shuffle=True)

print(len(train))
print(len(valid))
print(len(test))


train.to_csv(train_path)
test.to_csv(test_path)
valid.to_csv(dev_path)
