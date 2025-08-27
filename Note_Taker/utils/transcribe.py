import whisper
import random
import os
import threading
import queue
from utils.record import record
from datetime import datetime

class TranscriptionThread(threading.Thread):
    def __init__(self, file_queue):
        super().__init__()
        self.file_queue = file_queue
        self.model = None
        self.running = True
        self.daemon = True  # Thread will exit when main program exits
        
    def run(self):
        # Load the model only once when the thread starts
        self.model = whisper.load_model("base.en")
        
        while self.running:
            try:
                # Get a file from the queue, wait up to 1 second
                file_name = self.file_queue.get(timeout=1)
                
                # Process the file
                dt = datetime.now()
                dstr = dt.strftime("%A, %d. %B %Y %I:%M%p")
                result = self.model.transcribe(file_name)
                transcription = f"{dstr} - {result['text']}\n"
                
                # Write to transcription file
                with open("transcription.txt", "a") as trans_file:
                    trans_file.write(transcription)
                
                # Clean up the audio file
                os.remove(file_name)
                self.file_queue.task_done()
                
            except queue.Empty:
                # No files to process, continue waiting
                continue
            except Exception as e:
                print(f"Error in transcription thread: {str(e)}")

    def stop(self):
        self.running = False

# Global queue and thread instances
file_queue = queue.Queue()
transcription_thread = None

def ensure_transcription_thread():
    global transcription_thread
    if transcription_thread is None or not transcription_thread.is_alive():
        transcription_thread = TranscriptionThread(file_queue)
        transcription_thread.start()

def transcribe(file_name):
    model = whisper.load_model("base.en")
    result = model.transcribe(file_name)
    return result["text"]

def record_and_transcribe(seconds):
    # Ensure the transcription thread is running
    ensure_transcription_thread()
    
    # Generate unique filename
    file_name = str(random.randint(1000, 100000000)) + ".wav"
    print(f"Recording for {seconds} seconds")
    
    # Record audio
    record(seconds, file_name)
    
    # Add file to transcription queue
    file_queue.put(file_name)

def retrieve_transcription():
    trans_file = open("transcription.txt", "r")
    text = trans_file.read()
    trans_file.close()
    return text

def clear_transcription():
    trans_file = open("transcription.txt", "w")
    trans_file.write(" ")
    trans_file.close()

