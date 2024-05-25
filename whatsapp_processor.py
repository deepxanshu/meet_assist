from datetime import datetime
from io import BytesIO
import requests
from requests.auth import HTTPBasicAuth
from app.ai import advice, gpt_log
from pydub import AudioSegment
import pandas as pd
from app.boto_utils import upload_files_to_s3, fetch_and_process_user_data
from app.ai.speech import transcribe_audio
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from app.ai import gpt_surf
#from google.cloud import speech
import io

from main import  handle_user_input

app = Flask(__name__)

account_sid = 'your-twilio-accound-sid'
auth_token = 'your-twilio-auth-token'

sending_number = "your-sending-number"
conversations = {}  # Tracks the state of conversations with users

# Define conversation states
CONVERSATION_START = "start"
AWAITING_ACTION = "awaiting_action"
LOGGING_DATA = "logging_data"
SEEKING_ADVICE = "seeking_advice"
SURFING_INFO = "surfing_info"

# Keywords for actions
actions_keywords = {
    "log": LOGGING_DATA,
    "seek": SEEKING_ADVICE,
    "surf": SURFING_INFO,
    "add": LOGGING_DATA
}

MMM_FIELDS = ["Minutes", "Person Assigned", "Updates", "Status", "Date Assigned", "Due Date", "Key Takeaways", "Ageing", "Next Steps"]

# To track the progress of logging data for each user
user_field_progress = {}
all_meeting_data = []

# Function to send WhatsApp messages
def send_to_number(phone_number, body):
    client = Client(account_sid, auth_token)
    print(f"Sending message to {phone_number}: {body}")
    message = client.messages.create(from_=f"whatsapp:+{sending_number}", body=body, to=f"whatsapp:{phone_number}")

@app.route("/status", methods=["GET", "POST"])
def status_api():
    return "up and running"

@app.route("/whatsapp", methods=['POST'])
async def whatsapp_reply():
    incoming_msg = request.form.get('Body').strip().lower()
    mediaUrl0 = request.form.get('MediaUrl0')
    if mediaUrl0:
        response = download_media_from_twilio(mediaUrl0)
        incoming_msg = transcribe_audio(response)
    print("mediaUrl0", mediaUrl0)
    wa_id = request.form.get('WaId')
    phone_number = f"+{wa_id}"
    print(f"Received message from {phone_number}:\n{incoming_msg}")
    profile_name = request.form.get('ProfileName')
    print("profile_name", profile_name)

    if phone_number not in conversations:
        conversations[phone_number] = CONVERSATION_START

    current_state = conversations[phone_number]

    if current_state == CONVERSATION_START:
        welcome_user(phone_number, profile_name)
    else:
        await handle_user_input(phone_number, incoming_msg, current_state)

    return "OK", 200

def welcome_user(phone_number, profile_name):
    send_to_number(phone_number, f"Hi {profile_name}! I am Meet Assist 🤖, an AI-powered bot to help with your meeting details. What would you like to do? (log/seek/surf)")
    conversations[phone_number] = AWAITING_ACTION

MMM_PROMPT = ("Please provide the meeting details covering the following points:\n"
              "- Minutes\n"
              "- Person Assigned\n"
              "- Updates\n"
              "- Status\n"
              "- Date Assigned\n"
              "- Due Date\n"
              "- Key Takeaways\n"
              "- Next Steps\n")

def download_media_from_twilio(url):
    auth = HTTPBasicAuth(account_sid, auth_token)

    response = requests.get(url, auth=auth, allow_redirects=True)

    if response.status_code == 200:
        with open("downloaded_file", "wb") as file:
            ogg_buffer = io.BytesIO(response.content)
            return convert_ogg_to_wav(ogg_buffer)


def convert_ogg_to_wav(ogg_buffer):
    ogg_audio = AudioSegment.from_file(ogg_buffer, format="ogg")
    wav_buffer = io.BytesIO()
    ogg_audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)
    return wav_buffer

async def handle_user_input(phone_number, input_text, current_state):
    if current_state == AWAITING_ACTION:
        action = input_text.split()[0]  # Assumes first word is the action
        if action in actions_keywords:
            conversations[phone_number] = actions_keywords[action]
            print(action)
            if action == 'log':
                send_to_number(phone_number, MMM_PROMPT)
            elif action == 'seek':
                send_to_number(phone_number, f"What are you looking to {action}.")
            elif action == 'surf': 
                send_to_number(phone_number, f"What do you want to {action}.")
            else:
                send_to_number(phone_number, "Please provide the details for log")
        else:
            send_to_number(phone_number, "Sorry, I didn't understand that. Can you try asking differently? (log/seek/surf)")
    else:
        # Process based on the current action state
        if current_state == LOGGING_DATA:
            await process_logging_data(phone_number, input_text)
        elif current_state == SEEKING_ADVICE:
            await provide_advice(phone_number, input_text, all_meeting_data)
        elif current_state == SURFING_INFO:
            await surf_information(phone_number, input_text)

async def process_logging_data(phone_number, data):
    if data.lower() in ["yes", "y", "log"]:
        # Trigger when the user initiates logging or wants to add more data
        send_to_number(phone_number, "Please provide the details for log.")
    elif data.lower() in ["done", "exit"]:
        # User indicates they are finished adding data
        send_to_number(phone_number, "Thank you. Your logging session is complete.")
    else:
        # Interpret and map the comprehensive input
        interpreted_text = await gpt_log.interpret_user_input(data)
        mapped_data = await map_interpretation_to_fields(interpreted_text)
        all_meeting_data.append(mapped_data)
        await save_collected_data_to_csv(phone_number, all_meeting_data)
        send_to_number(phone_number, "Logged. Would you like to add more details or do something else? (add/seek/surf)")
        conversations[phone_number] = AWAITING_ACTION

async def map_interpretation_to_fields(interpreted_text):
    # Example parsing logic assuming GPT provides a structured text output
    mapped_data = {
        "Minutes": "",
        "Person Assigned": "",
        "Updates": "",
        "Status": "",
        "Date Assigned": "",
        "Due Date": "",
        "Key Takeaways": "",
        "Next Steps": "",
        "Additional Information": ""
    }
    
    for line in interpreted_text.split('\n'):
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        if key in mapped_data:
            mapped_data[key] = value
        else:
            # If the key is not recognized, add the information to 'Additional Information'
            mapped_data["Additional Information"] += f"{key}: {value}\n"
    
    return mapped_data


def parse_log_details(input_text):
    """
    Parses the user's input based on the expected format.
    Each detail is separated by a semicolon, mapped to the correct CSV column.
    """
    details_list = input_text.split(";")
    if len(details_list) != len(MMM_FIELDS):
        return None  # Or handle differently if you expect varying input lengths
    
    # Map the input to field names assuming the order matches MMM_FIELDS
    details = {MMM_FIELDS[i]: detail.strip() for i, detail in enumerate(details_list)}
    return details

async def provide_advice(phone_number, input_text, all_meeting_data):
    user_data_from_s3 = fetch_and_process_user_data(phone_number,"stashfin-storage-dev")
    all_meeting_data.append(user_data_from_s3)
    fianl_advice = advice.generate_advice_with_context(input_text, all_meeting_data)
    send_to_number(phone_number, f"{fianl_advice} \nWhat's else you need? (log/seek/surf)")
    conversations[phone_number] = AWAITING_ACTION


async def surf_information(phone_number, topic):
    # Call the GPT function to fetch information on the given topic
    surf_response = gpt_surf.generate_surf(topic)
    # Send the GPT response to the user
    send_to_number(phone_number, f"{surf_response} \nWhat's next? (log/seek/surf)")
    conversations[phone_number] = AWAITING_ACTION
    
async def save_collected_data_to_csv(phone_number, data):
    df = pd.DataFrame([data])  # Assuming data is a dictionary
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{phone_number}_data_{timestamp}.csv"
    
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0) 
    await upload_csv_document(buffer, filename, phone_number)
    
    return filename

async def upload_csv_document(file, filename, phone_number, s3_directory_base="webroot/meet-assist"):
        s3_directory = f"{s3_directory_base}/{phone_number}"
        try:
            await upload_files_to_s3(
                file, filename, "stashfin-storage-dev", s3_directory
                )
        
        except Exception as e:
            raise Exception(f"Upload failed due to an unexpected error: {str(e)}")
            
        return "document upload successfully"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

