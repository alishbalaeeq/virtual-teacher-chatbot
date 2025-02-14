import edge_tts

def text_to_speech(voice, text, output_file):
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    communicate.save_sync(output_file)
    print("Lecture audio generated!")