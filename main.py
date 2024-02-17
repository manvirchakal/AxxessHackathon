import sys
import serial
import csv
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Data Recording'
        self.initUI()
        self.serialPort = serial.Serial('/dev/cu.usbmodem142301', 9600, timeout=1)
        self.isRecording = False
        self.currentFile = None
        self.csvWriter = None
        self.currentData = []

    def initUI(self):
        self.setWindowTitle(self.title)

        # Layout
        layout = QVBoxLayout()

        # Start Record Button
        self.startButton = QPushButton('Start Recording', self)
        self.startButton.clicked.connect(self.start_recording)

        # Stop Record Button
        self.stopButton = QPushButton('Stop Recording', self)
        self.stopButton.clicked.connect(self.stop_recording)
        self.stopButton.setEnabled(False)  # Disable this button initially

        # Adding widgets to layout
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)

        # Set the layout
        self.setLayout(layout)

        # Show the App
        self.show()

    def start_recording(self):
        if not self.isRecording:
            self.isRecording = True
            self.stopButton.setEnabled(True)
            self.startButton.setEnabled(False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.currentFile = open(f'data/data_{timestamp}.csv', mode='w', newline='')
            self.csvWriter = csv.writer(self.currentFile)
            self.csvWriter.writerow(["X Acceleration", "Y Acceleration", "Z Acceleration"])  # Write header

    def stop_recording(self):
        if self.isRecording:
            self.isRecording = False
            self.stopButton.setEnabled(False)
            self.startButton.setEnabled(True)
            if self.currentFile:
                self.currentFile.close()
                self.currentFile = None
                self.currentData = []

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

    def closeEvent(self, event):
        self.serialPort.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    timer = QTimer()
    timer.timeout.connect(ex.record_data)
    timer.start(100)  # Adjust the timing based on how often you want to read from the serial port
    sys.exit(app.exec_())
