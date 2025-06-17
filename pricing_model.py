from sklearn.linear_model import LinearRegression
import pickle

def train_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    with open("pricing_model.pkl", "wb") as f:
        pickle.dump(model, f)
    return model

def load_model():
    with open("pricing_model.pkl", "rb") as f:
        model = pickle.load(f)
    return model

def predict_price(model, features):
    prediction = model.predict(features)
    return prediction[0]
