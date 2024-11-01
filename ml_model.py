
# File: ml_model.py
# Machine Learning Model to Predict Future Metrics
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Function to train the ML model
def train_model(data, variable1, variable2):
    """
    Train a machine learning model to predict future price differences.
    :param data: DataFrame containing historical metrics.
    :param variable1: Look-back period for historical high/low metrics.
    :param variable2: Look-forward period for future high/low metrics.
    :return: Trained model and accuracy score.
    """
    # Ensure variable1 and variable2 are passed correctly
    features = [
        f'Days_Since_High_Last_{variable1}_Days',
        f'%_Diff_From_High_Last_{variable1}_Days',
        f'Days_Since_Low_Last_{variable1}_Days',
        f'%_Diff_From_Low_Last_{variable1}_Days'
    ]
    X = data[features]
    y_high = data[f'%_Diff_From_High_Next_{variable2}_Days']
    y_low = data[f'%_Diff_From_Low_Next_{variable2}_Days']
    
    # Splitting data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(X, y_high, test_size=0.2, random_state=42)
    
    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Test the model
    y_pred = model.predict(X_test)
    accuracy = model.score(X_test, y_test)
    mse = mean_squared_error(y_test, y_pred)
    
    return model, accuracy, mse

# Function to make predictions using the trained model
def predict_outcomes(model, input_values):
    """
    Use the trained model to make predictions based on new input values.
    :param model: Trained model.
    :param input_values: New input values for prediction.
    :return: Predicted values for %_Diff_From_High_Next and %_Diff_From_Low_Next.
    """
    return model.predict([input_values])