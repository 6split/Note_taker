from utils.transcribe import record_and_transcribe, clear_transcription, retrieve_transcription, transcribe
import ollama, time
import threading

class Note_Taker:

    def __init__(self, lecture_name, debug_func):
        """
        Creates a note taker class, lecture_name is the name of the file excluding the .txt extension 
        """
        self.note_name = lecture_name + ".txt"
        self.lecture_name = lecture_name
        self.debug_func = debug_func
        pass
 
    def record_segment(self, seconds, transfer_len_limit=4000):
        record_and_transcribe(seconds)
        transcription = retrieve_transcription()
        trans_len = len(transcription)
        print(f"transcription length: {trans_len}")
        self.debug_func(f"transcription length: {trans_len}")
        if trans_len > transfer_len_limit:
            notes_thread = threading.Thread(target=self.transcription_to_notes)
            notes_thread.daemon = True  # Thread will exit when main program exits
            notes_thread.start()
        return
    
    def transcription_to_notes(self):
        """
        Uses Ollama to summarize the main transcription
        """
        self.debug_func("Starting Transcription -> Notes")
        transcription = retrieve_transcription()
        clear_transcription()
        start_time = time.time()
        stream = ollama.chat(
        model='gemma3n:e4b',
        messages=[
                {
                    'role': 'user',
                    'content': f'Here are the notes created so far: {self.retrieve_all_notes()}, Don\'t include timestamps in your response. Create an addition to the notes for this college class about {self.lecture_name} using this whisper transcription for a portion of the class: {transcription}',
                },
        ],
        stream=True,
        )
        msg = ""
        full_msg = ""
        for chunk in stream:
            msg += chunk['message']['content']
            full_msg += chunk['message']['content']
            while msg.__contains__("</think>"):
                think_index = str(msg).index("</think>")
                msg = msg[think_index + 8:]
        while msg.__contains__("</think>"):
            think_index = str(msg).index("</think>")
            msg = msg[think_index + 8:]
        while msg.__contains__("<think>"):
            think_index = str(msg).index("<think>")
            msg = msg[think_index + 7:]
        print(f"Deciding if response took {time.time() - start_time:.1f} seconds with ai response being: {full_msg}")
        self.debug_func("Finished Transcription -> Notes")
        try:
            with open(self.note_name, "a") as f:
                f.write(msg + "\n")
        except:
            file = open(self.note_name, "w")
            file.write(msg + "\n")
            file.close()
        return
    
    def create_test_transcript(self):
        transcribe("Lecture 1 Introduction to CS and Programming Using Python - MIT OpenCourseWare.mp3")

    def retrieve_all_notes(self):
        text = ""
        try:
            with open(self.note_name, 'r') as notes:
                text = notes.read()
        except:
            return ""
        return text

    def compound_notes(self):
        start_time = time.time()
        stream = ollama.chat(
        model='gemma3n:e4b',
        messages=[
                {
                    'role': 'user',
                    'content': f'Create a more comprehensive note sheet from these ones: {self.retrieve_all_notes()}, Don\'t include timestamps in your response. These notes are for a college lecture about {self.lecture_name}',
                },
        ],
        stream=True,
        )
        msg = ""
        full_msg = ""
        file = open(self.note_name, "w")
        file.write(" ")
        for chunk in stream:
            msg += chunk['message']['content']
            if chunk['message']['content']:
                file.write(chunk['message']['content'])
            full_msg += chunk['message']['content']
            while msg.__contains__("</think>"):
                think_index = str(msg).index("</think>")
                msg = msg[think_index + 8:]
        while msg.__contains__("</think>"):
            think_index = str(msg).index("</think>")
            msg = msg[think_index + 8:]
        while msg.__contains__("<think>"):
            think_index = str(msg).index("<think>")
            msg = msg[think_index + 7:]
        print(f"Deciding if response took {time.time() - start_time:.1f} seconds with ai response being: {full_msg}")
        file.write(msg + "\n")
        file.close()
        return



if __name__ == "__main__":
    n = Note_Taker("test")
    # # for i in range(5):
    # #     n.record_segment(60)
    # #     print(retrieve_transcription())
    n.compound_notes()



    
