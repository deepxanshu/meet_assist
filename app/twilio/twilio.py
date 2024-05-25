# from flask import Flask, jsonify, request
# # from twilio.twiml.messaging_response import MessagingResponse
# # from your_script import handle_advice_mode, generate_surf  # Adjust import based on your script structure
# app = Flask(__name__)


# @app.route('/')
# def home():
#     return jsonify({"message": "Hello, World!"})


# @app.route("/whatsapp", methods=['POST'])
# def whatsapp():
#     incoming_msg = request.values.get('Body', '').lower()
#     # resp = MessagingResponse()
#     msg = resp.message()

#     if 'advice' in incoming_msg:
#         # Extract the actual advice query from the message, if any
#         query = incoming_msg.replace('advice', '').strip()
#         advice_response = handle_advice_mode(query)  # Adjust this call as needed
#         msg.body(advice_response)
#     elif 'surf' in incoming_msg:
#         query = incoming_msg.replace('surf', '').strip()
#         surf_response = generate_surf(query)  # Adjust this call as needed
#         msg.body(surf_response)
#     else:
#         msg.body("Welcome to Meet Assist 🤖. Send 'advice' followed by your question for advice, or 'surf' for finance info.")

#     return str(resp)


# if __name__ == '__main__':
#     app.run(debug=True)