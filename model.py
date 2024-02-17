import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os
import glob

def load_data(folder):
    # Read all CSV files in the folder and concatenate into a single DataFrame
    all_files = glob.glob(os.path.join(folder, "*.csv"))
    df_list = []

    for file in all_files:
        df = pd.read_csv(file, index_col=None, header=0)
        df_list.append(df)

    return pd.concat(df_list, axis=0, ignore_index=True)

def main():
    # Load data
    correct_data = load_data('data_correct')
    incorrect_data = load_data('data_incorrect')

    # Assign labels (1 for correct, 0 for incorrect)
    correct_data['label'] = 1
    incorrect_data['label'] = 0

    # Combine datasets
    all_data = pd.concat([correct_data, incorrect_data])

    # Split data into features and labels
    X = all_data.drop('label', axis=1)
    y = all_data['label']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Initialize Random Forest classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)

    # Train the model
    clf.fit(X_train, y_train)

    # Make predictions on the test set
    predictions = clf.predict(X_test)

    # Print classification report
    print(classification_report(y_test, predictions))

if __name__ == "__main__":
    main()
