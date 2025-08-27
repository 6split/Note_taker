import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                           QStatusBar, QProgressBar, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from note_taker import Note_Taker
import threading

class RecordingThread(QThread):
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, note_taker):
        super().__init__()
        self.note_taker = note_taker
        self.is_running = True
        self.segment_duration = 60  # seconds

    def run(self):
        while self.is_running:
            self.note_taker.record_segment(self.segment_duration)
            self.status_update.emit("Recording in progress...")

    def stop(self):
        self.is_running = False

class ModernNoteTakerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.note_taker = None
        self.compound_thread = None
        self.recording_thread = None
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Note_App')
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create horizontal split layout
        split_layout = QHBoxLayout(central_widget)
        split_layout.setSpacing(10)
        split_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create debug panel on the left
        debug_frame = QFrame()
        debug_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        debug_layout = QVBoxLayout(debug_frame)
        
        # Debug panel title
        debug_title = QLabel("Console")
        debug_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 3px;
        """)
        debug_layout.addWidget(debug_title)
        
        # Debug text area
        self.debug_display = QTextEdit()
        self.debug_display.setReadOnly(True)
        self.debug_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        debug_layout.addWidget(self.debug_display)
        
        # Add debug frame to split layout with fixed width
        debug_frame.setFixedWidth(300)
        split_layout.addWidget(debug_frame)
        
        # Create main content area
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        split_layout.addWidget(main_container)

        # Title label
        title_label = QLabel("Lecture Note Taker")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 20px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Lecture name input section
        name_layout = QHBoxLayout()
        
        # Add label for lecture name
        name_label = QLabel("Lecture Name:")
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            margin-right: 10px;
        """)
        name_layout.addWidget(name_label)
        
        self.lecture_name_input = QLineEdit()
        self.lecture_name_input.setPlaceholderText("Enter lecture name...")
        self.lecture_name_input.setMinimumWidth(200)  # Set minimum width
        self.lecture_name_input.setMaximumWidth(400)  # Set maximum width
        self.lecture_name_input.setStyleSheet("""
            QLineEdit {
                color: #000000;
                background-color: #FFFFFF;
                selection-background-color: #2196F3;
            }
        """)
        
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_note_taker)
        name_layout.addWidget(self.lecture_name_input)
        name_layout.addWidget(self.create_button)
        main_layout.addLayout(name_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setEnabled(False)
        
        self.generate_button = QPushButton("Generate Notes")
        self.generate_button.clicked.connect(self.generate_notes)
        self.generate_button.setEnabled(False)
        
        # Add compound notes button
        self.compound_button = QPushButton("Compound Notes")
        self.compound_button.clicked.connect(self.start_compound_notes)
        self.compound_button.setEnabled(False)
        
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.compound_button)
        main_layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Notes display area
        notes_frame = QFrame()
        notes_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
                margin-top: 10px;
            }
        """)
        notes_layout = QVBoxLayout(notes_frame)
        
        notes_label = QLabel("Current Notes:")
        notes_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
        """)
        notes_layout.addWidget(notes_label)
        
        self.notes_display = QTextEdit()
        self.notes_display.setReadOnly(True)
        self.notes_display.setMinimumHeight(150)
        self.notes_display.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: white;
                color: #333333;
                font-size: 12px;
            }
        """)
        notes_layout.addWidget(self.notes_display)
        main_layout.addWidget(notes_frame)

        # Setup notes update timer
        self.notes_update_timer = QTimer()
        self.notes_update_timer.timeout.connect(self.update_notes_display)
        self.notes_update_timer.start(500)  # Update every 2 seconds

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #EEEEEE;
                color: #333333;
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to start")

        # Timer for progress bar
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_value = 0

    def toggle_recording(self):
        if not hasattr(self, 'is_recording'):
            self.is_recording = False

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.setText("Stop Recording")
        self.generate_button.setEnabled(False)
        self.status_bar.showMessage("Recording in progress...")
        self.log_debug("Starting new recording session")
        
        # Start recording thread
        self.recording_thread = RecordingThread(self.note_taker)
        self.recording_thread.status_update.connect(self.update_status)
        self.recording_thread.start()
        self.log_debug("Recording thread started")

        # Start progress bar
        self.progress_value = 0
        self.progress_timer.start(600)  # Update every 600ms for 60-second segments

    def stop_recording(self):
        self.is_recording = False
        self.record_button.setText("Start Recording")
        self.generate_button.setEnabled(True)
        self.log_debug("Stopping recording session")
        
        if self.recording_thread:
            self.recording_thread.stop()
            self.recording_thread.wait()
            self.log_debug("Recording thread stopped")
            
        self.progress_timer.stop()
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Recording stopped")

    def generate_notes(self):
        if self.is_recording:
            self.stop_recording()
        
        self.status_bar.showMessage("Generating notes...")
        try:
            notes_thread = threading.Thread(target=self.note_taker.transcription_to_notes)
            notes_thread.daemon = True  # Thread will exit when main program exits
            notes_thread.start()
            self.status_bar.showMessage("Notes generated successfully")
        except Exception as e:
            self.status_bar.showMessage(f"Error generating notes: {str(e)}")

    def update_status(self, message):
        self.status_bar.showMessage(message)

    def update_progress(self):
        self.progress_value = (self.progress_value + 1) % 100
        self.progress_bar.setValue(self.progress_value)
        
    def log_debug(self, message):
        """Add a timestamped message to the debug console"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        debug_message = f"[{timestamp}] {message}\n"
        self.debug_display.append(debug_message)
        # Auto-scroll to bottom
        self.debug_display.verticalScrollBar().setValue(
            self.debug_display.verticalScrollBar().maximum()
        )

    def update_notes_display(self):
        if self.note_taker and hasattr(self.note_taker, 'note_name'):
            try:
                if os.path.exists(self.note_taker.note_name):
                    with open(self.note_taker.note_name, 'r') as f:
                        current_notes = f.read()
                        if current_notes != self.notes_display.toPlainText():
                            self.notes_display.setPlainText(current_notes)
            except Exception as e:
                self.log_debug(f"Error reading notes: {str(e)}")
                self.status_bar.showMessage(f"Error reading notes: {str(e)}")
                
    def start_compound_notes(self):
        if not self.note_taker:
            self.status_bar.showMessage("Create a note taker first")
            return
        self.log_debug("User Clicked Compound")
        self.compound_button.setEnabled(False)
        self.status_bar.showMessage("Compounding notes...")
        
        # Create and start the compound notes thread
        compound_thread = threading.Thread(target=self.run_compound_notes)
        compound_thread.daemon = True
        compound_thread.start()
        self.log_debug("Compound Notes Thread Started")
        
    def run_compound_notes(self):
        try:
            self.note_taker.compound_notes()
            # Update the status in the main thread
            self.status_bar.showMessage("Notes compounded successfully")
        except Exception as e:
            self.status_bar.showMessage(f"Error compounding notes: {str(e)}")
        finally:
            self.compound_button.setEnabled(True)
            self.log_debug("Finished Compounding Notes")

    def create_note_taker(self):
        name = self.lecture_name_input.text().strip()
        if name:
            self.note_taker = Note_Taker(name, self.log_debug)
            self.record_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.compound_button.setEnabled(True)
            self.status_bar.showMessage("Note taker created successfully")
            self.lecture_name_input.setEnabled(False)
            self.create_button.setEnabled(False)
            
            self.log_debug(f"Created new Note Taker for lecture: {name}")
            # Initial notes load if file exists
            self.update_notes_display()
        else:
            self.status_bar.showMessage("Please enter a lecture name")
            self.log_debug("Error: No lecture name provided")

def main():
    app = QApplication(sys.argv)
    window = ModernNoteTakerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
