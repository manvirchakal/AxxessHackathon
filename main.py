import sys
import os
import serial
import csv
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPalette
import pandas as pd
from model import load_data, main, predict  # Import main function from model.py

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Data Recording'
        self.initUI()
        self.serialPort = serial.Serial('/dev/cu.usbmodem142401', 9600, timeout=1)
        self.isRecording = False
        self.currentFile = None
        self.csvWriter = None
        self.currentData = []
        self.autoStopTimer = QTimer(self)
        self.autoStopTimer.setSingleShot(True)
        self.autoStopTimer.timeout.connect(self.stop_recording)

    def initUI(self):
        self.setWindowTitle(self.title)

        # Layout
        layout = QVBoxLayout()

        # Record Correct Button
        self.recordCorrectButton = QPushButton('Record Correct', self)
        self.recordCorrectButton.clicked.connect(lambda: self.start_recording("correct"))

        # Record Incorrect Button
        self.recordIncorrectButton = QPushButton('Record Incorrect', self)
        self.recordIncorrectButton.clicked.connect(lambda: self.start_recording("incorrect"))

        # Stop Record Button
        self.stopButton = QPushButton('Stop Recording', self)
        self.stopButton.clicked.connect(self.stop_recording)
        self.stopButton.setEnabled(False)  # Disable this button initially

        # Adding widgets to layout
        layout.addWidget(self.recordCorrectButton)
        layout.addWidget(self.recordIncorrectButton)
        layout.addWidget(self.stopButton)
        
        # Train Model Button
        self.trainModelButton = QPushButton('Train Model', self)
        self.trainModelButton.clicked.connect(self.train_model)
        layout.addWidget(self.trainModelButton)

         # Predict Button
        self.predictButton = QPushButton('Predict Movement', self)
        self.predictButton.clicked.connect(self.start_prediction_recording)
        layout.addWidget(self.predictButton)

        '''# Add a label for prediction result
        self.predictionResult = QLabel(self)
        self.predictionResult.setText("Prediction Result")
        self.predictionResult.setAutoFillBackground(True)
        layout.addWidget(self.predictionResult)'''

        # Set the layout
        self.setLayout(layout)

        # Show the App
        self.show()

    def start_recording(self, recordType):
        if not self.isRecording:
            self.isRecording = True
            self.stopButton.setEnabled(True)
            self.recordCorrectButton.setEnabled(False)
            self.recordIncorrectButton.setEnabled(False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            directory = f'data_{recordType}'
            if not os.path.exists(directory):
                os.makedirs(directory)
            self.currentFile = open(f'{directory}/data_{recordType}_{timestamp}.csv', mode='w', newline='')
            self.csvWriter = csv.writer(self.currentFile)
            self.csvWriter.writerow(["X Acceleration", "Y Acceleration", "Z Acceleration"])  # Write header
            self.autoStopTimer.start(3000)  # Start the timer for 3 seconds

    def stop_recording(self):
        if self.isRecording:
            self.isRecording = False
            self.stopButton.setEnabled(False)
            self.recordCorrectButton.setEnabled(True)
            self.recordIncorrectButton.setEnabled(True)
            if self.currentFile:
                self.currentFile.close()
                self.currentFile = None
                self.currentData = []
            self.autoStopTimer.stop()  # Stop the timer

    def record_data(self):
        if self.isRecording and self.serialPort.in_waiting > 0:
            try:
                line = self.serialPort.readline().decode('utf-8').rstrip()
                if line.startswith("X Acceleration:") or line.startswith("Y Acceleration:") or line.startswith("Z Acceleration:"):
                    accel_value = float(line.split(": ")[1])
                    self.currentData.append(accel_value)
                    if len(self.currentData) == 3:  # Check if all three values are collected
                        self.csvWriter.writerow(self.currentData)  # Write the complete set of values
                        self.currentData = []  # Reset for next set of values
                    print(line)  # Optional, for debugging
            except UnicodeDecodeError:
                pass  # Skip lines that cannot be decoded

    def train_model(self):
        # Call the main function from model.py to train the model
        main()

    def closeEvent(self, event):
        self.serialPort.close()
        event.accept()

    def start_prediction_recording(self):
        print("Starting prediction recording...")
        if not self.isRecording:
            self.isRecording = True
            self.currentFile = open('prediction_data.csv', mode='w', newline='')
            self.csvWriter = csv.writer(self.currentFile)
            self.csvWriter.writerow(["X Acceleration", "Y Acceleration", "Z Acceleration"])

            # Connect the timeout signal to the stop recording method
            self.autoStopTimer.timeout.connect(self.stop_recording_prediction)
            self.autoStopTimer.start(3000)  # Record for 3 seconds

    def stop_recording_prediction(self):
        print("Stopping prediction recording...")
        if self.isRecording:
            self.isRecording = False
            self.csvWriter = None
            self.currentFile.close()
            self.currentFile = None
            self.analyze_prediction_data()

    def analyze_prediction_data(self):
        filename = 'prediction_data.csv'
        #pause for a few seconds to ensure the file is saved

        print("Analyzing prediction data...")
        # Load the saved data
        predict_df = pd.read_csv(filename)

        # Format the data as needed for prediction
        formatted_data = predict_df.to_numpy().flatten()

        # Predict using the formatted data
        prediction = predict([formatted_data])

        # Set prediction result
        self.set_prediction_result(prediction == 1)

    def set_prediction_result(self, is_correct):
        # Update UI based on prediction
        if is_correct:
            self.predictionResult.setText("Movement is correct")
            self.setStyleSheet("background-color: green;")
        else:
            self.predictionResult.setText("Movement is incorrect")
            self.setStyleSheet("background-color: red;")
        QTimer.singleShot(1000, lambda: self.setStyleSheet(""))

        
        

    '''def predict_movement(self):
        # Start collecting data for prediction
        self.currentData = []
        self.collectingData = True
        QTimer.singleShot(3000, self.stop_collecting_data)  # Adjust time as needed
        print("Started collecting data for prediction...")

    def stop_collecting_data(self):
        # Stop data collection and make a prediction
        self.collectingData = False
        print(f"Collected Data: {self.currentData}")
        formatted_data = self.format_data_for_prediction(self.currentData)
        print(f"Predicting movement for data: {formatted_data}")
        prediction = predict(formatted_data)

        # Set prediction result
        if prediction == 1:
            self.set_prediction_result(True)
        else:
            self.set_prediction_result(False)

    def format_data_for_prediction(self, data):
        # Assuming each prediction is based on a single set of [X, Y, Z] readings
        # Take the most recent [X, Y, Z] reading for prediction
        if len(data) >= 3:
            latest_reading = data[-3:]  # Get the last 3 values (X, Y, Z)
        else:
            # If not enough data was captured, use default values (e.g., [0, 0, 0])
            latest_reading = [0, 0, 0]

        return latest_reading  # Return the latest reading as a list
    
    def set_prediction_result(self, is_correct):
        # Update UI based on prediction
        if is_correct:
            # Flash green for correct
            # Example: Change background color to green
            self.setStyleSheet("background-color: green;")
        else:
            # Flash red for incorrect
            # Example: Change background color to red
            self.setStyleSheet("background-color: red;")

        # Reset background color after a short delay
        QTimer.singleShot(1000, lambda: self.setStyleSheet(""))'''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    timer = QTimer()
    timer.timeout.connect(ex.record_data)
    timer.start(100)  # Adjust the timing based on how often you want to read from the serial port
    sys.exit(app.exec_())
