from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPalette
from model import load_data, main, predict  # Import main function from model.py
import pandas as pd
import sys

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Analysis'
        self.currentFile = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)

        # Layout
        layout = QVBoxLayout()

        #button to start analysis
        self.startAnalysisButton = QPushButton('Start Analysis', self)
        self.startAnalysisButton.clicked.connect(self.start_analysis)
        layout.addWidget(self.startAnalysisButton)

        # Add a label for analysis result
        self.analysisResultLabel = QLabel('Analysis Result: ', self)
        layout.addWidget(self.analysisResultLabel)

        # Set the layout
        self.setLayout(layout)

        self.show()

    def start_analysis(self):
        filename = 'prediction_data.csv'
        # Load the saved data
        predict_df = pd.read_csv(filename)

        # Flatten the data to match the training format
        # Assuming each observation is a row in the DataFrame
        formatted_data = predict_df.values.flatten()
        # Reshape the data to have 3 columns (X, Y, Z accelerations)
        formatted_data = formatted_data.reshape(-1, 3)

        print(formatted_data)

        # Predict using the formatted data
        prediction = predict(formatted_data)

        # Set prediction result
        self.set_prediction_result(prediction == 1)

    def set_prediction_result(self, is_correct):
        if is_correct:
            self.analysisResultLabel.setText('Analysis Result: Correct Movement')
            self.analysisResultLabel.setStyleSheet('color: green')
        else:
            self.analysisResultLabel.setText('Analysis Result: Incorrect Movement')
            self.analysisResultLabel.setStyleSheet('color: red')
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
