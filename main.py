import sys
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QMessageBox

class MovementAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serialPort = None

    def initUI(self):
        # Layout
        layout = QVBoxLayout()

        # ... [Add the existing UI components here as before]

        # Button to start recording data
        self.recordButton = QPushButton('Record Data', self)
        self.recordButton.clicked.connect(self.recordData)
        layout.addWidget(self.recordButton)

        # Set the layout
        self.setLayout(layout)
        self.setWindowTitle('Physical Therapy Movement Analyzer')

    def analyzeMovement(self):
        selected_movement = self.movementComboBox.currentText()
        # Placeholder for movement analysis logic
        self.resultLabel.setText(f"Analyzing {selected_movement}... (not yet implemented)")

    def recordData(self):
        try:
            self.serialPort = serial.Serial('/dev/cu.usbmodem142301', 9600, timeout=1)  # Replace 'COM3' with your Arduino's port
            self.readData()
        except serial.SerialException:
            QMessageBox.critical(self, "Serial Port Error", "Could not open the serial port.")
            if self.serialPort:
                self.serialPort.close()
                self.serialPort = None

    def readData(self):
        # Read data from the serial port
        if self.serialPort:
            while True:
                line = self.serialPort.readline().decode('utf-8').rstrip()
                if line.startswith("X Acceleration"):
                    # Process the line (e.g., store it, display it, etc.)
                    print(line)  # For now, just print it
                    # Add logic here to handle the data as per your application's need

# Initialize and run the application
app = QApplication(sys.argv)
ex = MovementAnalyzer()
ex.show()
sys.exit(app.exec_())
