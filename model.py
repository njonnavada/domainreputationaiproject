# model.py

from sklearn.tree import DecisionTreeClassifier
from data import get_training_data

def train_model():
    X, y = get_training_data()

    model = DecisionTreeClassifier()
    model.fit(X, y)

    return model


def predict(model, domain):
    features = [[
        domain["openRate"],
        domain["bounceRate"],
        domain["complaintRate"]
    ]]

    return model.predict(features)[0]