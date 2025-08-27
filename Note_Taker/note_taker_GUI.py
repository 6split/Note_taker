import tkinter as tk
from tkinter import ttk
import threading
from note_taker import Note_Taker

class NoteTakerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lecture Note Taker")
        self.root.geometry("400x300")
        
        self.note_taker = None
        self.recording = False
        self.recording_thread = None

        # Create lecture name input
        self.name_frame = ttk.Frame(root)
        self.name_frame.pack(pady=10)
        ttk.Label(self.name_frame, text="Lecture Name:").pack(side=tk.LEFT)
        self.lecture_name = ttk.Entry(self.name_frame)
        self.lecture_name.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.name_frame, text="Create", command=self.create_note_taker).pack(side=tk.LEFT)

        # Create recording controls
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(pady=20)
        self.record_button = ttk.Button(self.control_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(side=tk.LEFT, padx=5)
        self.generate_button = ttk.Button(self.control_frame, text="Generate Notes", command=self.generate_notes)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = ttk.Label(root, text="Enter lecture name to begin")
        self.status_label.pack(pady=10)

    def create_note_taker(self):
        name = self.lecture_name.get().strip()
        if name:
            self.note_taker = Note_Taker(name)
            self.status_label.config(text="Note taker created successfully")
        else:
            self.status_label.config(text="Please enter a lecture name")

    def toggle_recording(self):
        if not self.note_taker:
            self.status_label.config(text="Create a note taker first")
            return

        if not self.recording:
            self.recording = True
            self.record_button.config(text="Stop Recording")
            self.status_label.config(text="Recording...")
            self.recording_thread = threading.Thread(target=self.record_loop)
            self.recording_thread.start()
        else:
            self.recording = False
            self.record_button.config(text="Start Recording")
            self.status_label.config(text="Recording stopped")

    def record_loop(self):
        while self.recording:
            self.note_taker.record_segment(60)

    def generate_notes(self):
        if not self.note_taker:
            self.status_label.config(text="Create a note taker first")
            return
        
        if self.recording:
            self.toggle_recording()
        
        self.status_label.config(text="Generating notes...")
        try:
            self.note_taker.transcription_to_notes()
            self.status_label.config(text="Notes generated successfully")
        except Exception as e:
            self.status_label.config(text=f"Error generating notes: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteTakerGUI(root)
    root.mainloop()