import speech_recognition as sr

r = sr.Recognizer()

def record_text():
    
    while(1):    
        
        try:
            
            with sr.Microphone() as source2:
                
                r.adjust_for_ambient_noise(source2, duration=0.2)
                
                audio2 = r.listen(source2)
                
                # Using google to recognize audio
                text = r.recognize_google(audio2)
                
                return text
        except sr.RequestError as e:
            print("Could not request results: {0}".format(e))
            
        except sr.UnknownValueError:
            print("unknown error occurred")

    return
def output_text(text):
    f = open("output.txt","a")
    f.write(text)
    f.write("\n")
    f.close()
    return
def main():
    if(1):
        text = record_text()
        output_text(text)

        print("Wrote text")
    return "voice to text ended"

if __name__ == "__main__":
    main()