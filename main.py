from datetime import datetime
import os
import glob
import pandas as pd
from app import handler
from app.ai import gpt_surf
from itertools import cycle

#voice
from app.ai import advice, gpt_surf
import speech_recognition as sr
from app.ai.speech import capture_audio_from_mic, transcribe_audio
import pyttsx3
from datetime import datetime
import os
import glob
import pandas as pd
# Assuming 'advice', 'handler', and 'gpt_surf' are modules in your 'app' package
from app import handler
from itertools import cycle

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
#tts_engine = pyttsx3.init()

follow_up_prompts = [
    "How else can I assist you?",
    "Any other questions on your mind?",
    "What more would you like to know?",
    "Do you have another query?",
    "How can I help you further?"
]

# Create an iterator that cycles through the follow-up prompts
follow_up_cycle = cycle(follow_up_prompts)

def get_next_follow_up():
    """Get the next follow-up prompt."""
    return next(follow_up_cycle)

def ask(question, can_give_advice=False):
    """
    Enhanced ask function that allows for 'exit' and 'advice' options.
    """
    while True:
        user_input = input(f"{question} (Type 'exit' to quit, 'advice' to ask a question): ").strip()
        if user_input.lower() == "exit":
            print("Exiting program...")
            exit(0)
        elif user_input.lower().startswith("advice") and can_give_advice:
            advice_question = user_input[6:].strip()  # Extract the question part
            if advice_question:
                generate_advice(advice_question)  # Assume this function is implemented to handle advice
            else:
                print("Please type a question after 'advice'.")
            continue
        else:
            return user_input

def generate_advice(question):
    """
    Generates advice based on the user's question using GPT. This function needs to be tailored
    to search through the collected data and use it as context for the GPT query.
    """
    # Example placeholder implementation
    print(f"Generating advice for question: {question}")
    # Here you would include logic to parse the collected data for context,
    # and to form a prompt for GPT based on the question and that context.
    # The GPT-generated advice would then be printed or otherwise communicated to the user.

last_entry = {}  # Dictionary to store the last entered values for each field
user_informed_about_suggestions = False

def exit_program(all_meeting_data, meeting_type):
    save_meeting_data(all_meeting_data, meeting_type)
    print("Exiting program after saving...")
    exit(0)

def is_exit_command(input_str):
    return input_str.lower() in ['exit', 'exut', 'exi', 'exot', 'quit', 'close', 'bye', 'tada']

def ask_with_suggestion(field_name, suggestion='', all_meeting_data=None, meeting_type=None):
    global user_informed_about_suggestions
    prompt = f"Enter {field_name}"
    if suggestion and not user_informed_about_suggestions:
        prompt += f" (or press Enter to use '{suggestion}')"
    user_input = input(f"{prompt}: ").strip()
    
    if is_exit_command(user_input):
        exit_program(all_meeting_data, meeting_type)
    
    if user_input == '' and suggestion:
        use_last_suggestion = ask_yes_or_no("Would you like to keep it blank or use the last suggestion?")
        return suggestion if use_last_suggestion else ''
    
    user_informed_about_suggestions = True
    return user_input

def collect_data_predefined(meeting_type, serial_number, all_meeting_data):
    fields = {
        "MMM": ["Minutes", "Person Assigned", "Updates", "Status", "Date Assigned", "Due Date", "Key Takeaways", "Ageing", "Next Steps"],
        "Client Meet": ["Place", "Company Name", "Agenda", "Attendees from Stashfin", "Attendees from the Client Company", "Key Takeaways", "Next Steps", "Summarize", "Anything Else"],
    }
    collected_data = {"Serial Number": serial_number}
    for field in fields[meeting_type]:
        suggestion = last_entry.get(field, '')
        collected_data[field] = ask_with_suggestion(field, suggestion, all_meeting_data, meeting_type)
        last_entry[field] = collected_data[field]
        
    return collected_data

def ask_for_meeting_type():
    """
    Ask the user for the meeting type and handle common variations or misspellings.
    """
    while True:
        user_input = ask("Enter the meeting type (MMM or Client Meet):")
        meeting_type = handler.get_meeting_type(user_input)
        if meeting_type:
            return meeting_type
        else:
            print("Unrecognized meeting type. Please enter 'MMM' or 'Client Meet.'")

def ask_for_voice_or_text():
    """
    Ask the user for proceeding in voice or text.
    """
    while True:
        user_input = ask("Enter 'voice' or 'text':")
        chat_type = handler.get_chat_type(user_input)
        if chat_type:
            return chat_type
        else:
            print("Unrecognized chat type. Please enter 'text' or 'voice'")

def ask_yes_or_no(question):
    """
    Ask a yes/no question and accept variations of 'yes' and 'no' as responses.
    """
    while True:
        user_input = input(f"{question} (yes/no): ").strip().lower()
        if handler.is_affirmative(user_input):
            return True
        elif handler.is_negative(user_input):
            return False
        else:
            print("Unrecognized response. Please answer with yes or no.")
   
def save_meeting_data(all_meeting_data, meeting_type):
    if all_meeting_data:  # Check if there's any data to save
        df = pd.DataFrame(all_meeting_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{meeting_type}_data_{timestamp}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Data saved to {filename}. Thank you for using the Meet Assist!")
        return filename  # Return the filename for later use
    else:
        print("No meeting data collected.")
        return None
    
def get_last_document(meeting_type):
    list_of_files = glob.glob(f'{meeting_type}_data_*.xlsx')
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def is_casual_inquiry(query):
    casual_phrases = [
    'yo',
    'what up',
    'sup',
    'theek ho',
    'how are you',
    'what’s up',
    'okay',
    'hi',
    'hello',
    'good morning',
    'good afternoon',
    'good evening',
    'bye',
    'see ya',
    'thanks',
    'thank you',
    'lol',
    'haha',
    'that’s funny',
    'i’m bored',
    'tell me a joke',
    'what’s your name',
    'who made you',
    'what can you do'
]
    return any(phrase in query.lower() for phrase in casual_phrases)

def handle_advice_mode(all_meeting_data, chat_type):
    
    advice_count = 0  
    
    while True:
        if chat_type == "voice":
            print("Entering advice mode. Type 'exit' to return to the main menu.")
            tts_engine.say("Entering advice mode. Type 'exit' to return to the main menu.")
            tts_engine.runAndWait()
            
        if advice_count == 0:
            if chat_type == "voice":
                print("What do you need advice on? ", end="")
                tts_engine.say("What do you need advice on?")
                tts_engine.runAndWait()
                audio_data = capture_audio_from_mic()
                advice_query = transcribe_audio(audio_data)
            else:
                advice_query = input("What do you need advice on? ").strip()
                
        else:
            # Use varied follow-up prompts after the first query
            follow_up = get_next_follow_up()
            if chat_type == "voice":
                print(f"{follow_up} ", end="")
                tts_engine.say(follow_up)
                tts_engine.runAndWait()
                audio_data = capture_audio_from_mic()
                advice_query = transcribe_audio(audio_data)
            else:
                advice_query = input(f"{follow_up} ").strip()
                advice_query = input().strip()      
        
        if is_exit_command(advice_query):
            print("Exiting advice mode...")
            break
        
        fianl_advice = advice.generate_advice_with_context(advice_query, all_meeting_data)
        print(fianl_advice)
        
        advice_count += 1

def handle_surf_mode(chat_type):
    print("Entering surf mode. Type 'exit' to return to the main menu.")
    while True:
        if chat_type == "voice":
            # Fetch the next follow-up prompt for voice
            follow_up_prompt = get_next_follow_up()
            tts_engine.say(follow_up_prompt)
            tts_engine.runAndWait()
            # Capture and transcribe the user's voice input
            audio_data = capture_audio_from_mic()
            surf_query = transcribe_audio(audio_data)
        else:
            # Fetch and display the next follow-up prompt for text input
            surf_query = input(get_next_follow_up()()).strip()
        
        if is_exit_command(surf_query):
            print("Exiting surf mode...")
            break
        
        # Process the surf query using a hypothetical generate_surf function
        surf_response = gpt_surf.generate_surf(surf_query)
        print(surf_response)
        
        # Manually ask the user to enter 'yes' or 'no' in the terminal to decide whether to continue.
        # This part is outside the voice/text if-else block, so it applies to both modes equally.
        continue_response = input("Do you need more assistance? (yes/no): ").strip().lower()
        
        # Check the user's response and exit the loop if they do not want more assistance.
        if continue_response not in ['yes', 'y']:
            print("Exiting surf mode...")
            break

        
def get_user_choice_for_document(last_document):
    print(f"Do you want to load the last saved document ({last_document})?")
    choice = input("Type 'last' to load the last document, 'other' to specify a document, or 'none' to continue without loading: ").strip().lower()
    return choice

# for twilio / whatsapp

def handle_user_input(input_text):
    # Example logic based on input_text
    if input_text.lower() in ["hello", "hi", "yo", "how are you"]:
        return "Hi there! How can I assist you today?"
    else:
        return "Sorry, I didn't understand that. Can you try asking differently?"
    
    
# for voice speech
surf_keywords = ["browse", "surf", "web"]
seek_keywords = ["advice", "help", "seek"]
log_keywords = ["record", "log", "add"]
def process_voice_command():
    # Capture audio from the microphone
    audio_data = capture_audio_from_mic()
    
    # Transcribe the captured audio using Whisper
    command_text = transcribe_audio(audio_data)
    
    # Process the transcribed command
    if any(keyword in command_text for keyword in surf_keywords):
        return "surf"
        # Here, add your logic to process the 'surf' command
    elif any(keyword in command_text for keyword in seek_keywords):
        return "seek"
        # Here, add your logic to process the 'seek' command
    elif any(keyword in command_text for keyword in log_keywords):
        return "log"
        # Here, add your logic to process the 'log' command
    else:
        return "Command not recognized."
    
    # # Use text-to-speech to vocalize the response
    # tts_engine.say(response)
    # tts_engine.runAndWait()
    
def main():
    print("Hi, I am Meet Assist 🤖, AI powered bot to log or help w/ your meeting deets")

    meeting_type = ask_for_meeting_type()
    last_document = get_last_document(meeting_type)
    all_meeting_data = []

    if last_document:
        user_choice = get_user_choice_for_document(last_document)
        
        if user_choice == 'last':
            all_meeting_data = pd.read_excel(last_document).to_dict(orient='records')
            serial_number = len(all_meeting_data) + 1
        elif user_choice == 'other':
            specified_document = input("Please enter the path to the document: ").strip()
            try:
                all_meeting_data = pd.read_excel(specified_document).to_dict(orient='records')
                serial_number = len(all_meeting_data) + 1
            except Exception as e:
                print(f"Error loading specified document: {e}")
                print("Continuing without loading a document.")
        elif user_choice == 'none':
            pass  # Proceed without loading any document
        else:
            print("Unrecognized option. Assuming you want to continue without loading a document.")
    else:
        print("No previous document found. Starting fresh.")
    
    while True:
        chat_type = ask_for_voice_or_text()
        if chat_type == "voice":
            print("Do you want to 'log' meeting data, 'seek' advice, or 'surf' finance information? (log/seek/surf): ")
            tts_engine.say("Do you want to log meeting data, seek advice, or surf finance information? Say log, seek, surf.")
            tts_engine.runAndWait()
            user_action = process_voice_command()
        
        else :
            user_action = input("Do you want to 'log' meeting data, 'seek' advice, or 'surf' finance information? (log/seek/surf/exit): ").strip()
        
        if is_exit_command(user_action):
            print("Exiting program...")
            return  # This ensures the program exits when 'exit' is typed

        action = handler.get_action(user_action)

        if action == "seek":
            handle_advice_mode(all_meeting_data, chat_type)  # Make sure this function is defined or adjusted accordingly
            continue
        elif action == "surf":
            handle_surf_mode(chat_type)  # Make sure this function is defined or adjusted accordingly
        elif action == "log":
            while True:
                serial_number = 1
                collected_data = collect_data_predefined(meeting_type, serial_number, all_meeting_data)  # Adjust this function as necessary
                all_meeting_data.append(collected_data)
                serial_number += 1

                if chat_type == "voice":
                    print("Do you want to add more details, seek advice, or exit? (add/seek): ")
                    tts_engine.say("Do you want to add more details, seek advice, or exit? (add/seek): ")
                    tts_engine.runAndWait()
                    next_action = process_voice_command()
                else:
                    next_action = input("Do you want to add more details, seek advice, or exit? (add/seek): ").strip().lower()
                
                
                if is_exit_command(next_action):
                    print("Exiting program...")
                    return
                
                action = handler.get_action(next_action)
                if next_action == "exit":
                    last_document = save_meeting_data(all_meeting_data, meeting_type)
                    return
                elif any(keyword in next_action for keyword in surf_keywords):
                    handle_surf_mode(chat_type)
                elif any(keyword in next_action for keyword in seek_keywords):
                    handle_advice_mode(all_meeting_data, chat_type)
                elif any(keyword in next_action for keyword in log_keywords):
                    print("Add more data.")
                elif next_action != "add":
                    print("Unrecognized option. Assuming you want to add more data.")
        else:
            print("Unrecognized action. Please type 'log' to log meeting data, 'seek' for advice, or 'surf' for finance information.")

if __name__ == "__main__":
    main()