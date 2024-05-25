from twilio.rest import Client

account_sid = 'your-twilio-account-sid'
auth_token = 'your-twilio-auth-token'
client = Client(account_sid, auth_token)

sending_number = "your-sending-number"

receiving_number = "" # deepanshu

body = """Hi, I'm Meet Assist 👋
I can help with your meeting log and surf around the fintech web."""

message = client.messages.create(
  from_=f"whatsapp:+{sending_number}",
  body=body,
  to=f"whatsapp:+{receiving_number}"
)
print(message)
print(message.sid)