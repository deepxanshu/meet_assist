# Meet Assist

Meet Assist is an AI-powered assistant designed to log meeting details, provide advice, and offer finance information via text or voice interaction.

## Features

- **Meeting Logging**: Record meeting details including minutes, assigned persons, and action items.
- **Advice Mode**: Seek advice based on past meeting data.
- **Finance Information**: Surf through finance information using voice commands.

## Installation

To install Meet Assist, follow these steps:

1. Clone the repository to your local machine.
2. Ensure you have Python 3.10 or higher installed.
3. Install the required dependencies by running `pip install -r requirements.txt`.

## Usage

1. Run `main.py` to start Meet Assist.
2. Follow the prompts to log meeting details, seek advice, or surf finance information.

## Dependencies

- pandas
- Flask
- pyttsx3
- SpeechRecognition
- Twilio

Refer to `requirements.txt` for a complete list of dependencies.

## Docker Support

A `Dockerfile` is included for containerization and easy deployment.

## Configuration

- Configure Twilio WhatsApp integration in `whatsapp_processor.py`.
- Set up AWS credentials for `boto_utils` if using S3 services.

## Credentials and Keys Configuration

To fully use Meet Assist, you'll need to configure the following credentials and API keys:

### Twilio Credentials

1. Sign up for a Twilio account if you don't already have one.
2. Create a new project in the Twilio console.
3. Obtain your `Account SID` and `Auth Token` from the Twilio console.
4. Configure these values in `whatsapp_processor.py`.

### AWS Credentials for S3

1. Create an AWS account and set up an IAM user with S3 access.
2. Obtain your `Access Key ID` and `Secret Access Key`.
3. Configure your AWS credentials in a `.env` file or by setting environment variables.

### OpenAI API Key

1. Sign up for an OpenAI account to access their API.
2. Obtain your API key from the OpenAI console.
3. Store your OpenAI API key in a secure location and reference it in your application code as needed.

### Whisper (Optional)

If using Whisper for speech recognition or any other feature that requires it:
1. Follow the installation and usage instructions provided by the Whisper project.
2. Ensure you have the necessary credentials if required by Whisper's API.

## Development

To contribute to Meet Assist, create a branch from `main` and submit a pull request with your changes.

## License

Specify the license under which Meet Assist is released.

## Contact

Provide contact information for users to report issues or seek support.

---

For a detailed guide on each feature and configuration steps, refer to the documentation in the respective modules.