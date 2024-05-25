
def generate_meeting_questions(meeting_type):
    system_message = f"""
    You are an assistant specialized in planning and documenting meetings. 
    Your task is to generate a set of questions or data points that should be collected for a {meeting_type} meeting.
    The response should be structured as a list of items, each describing a distinct aspect of the meeting that needs attention. 
    For 'Monday Morning Meeting i.e. MMM' meetings, focus on goals, challenges, decisions, and action items and 
    stuff like "Serial Number", "Minutes", "Person Assigned", "Status", "Date Assigned", "Due Date", "Key Takeaways", "Next Steps".
    
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"What questions or data points should be collected for a {meeting_type} meeting?"}
    ]
    
    functions = [{"name": "generate_meeting_questions"}]
    function_call = {"name": "generate_meeting_questions"}

    # Assuming the function chat_completion_request is defined elsewhere and correctly implemented
    chat_response = ai.chat_completion_request(messages, functions=functions, function_call=function_call, model=GPT_MODEL)
    try:
        response_content = chat_response.json()
        generated_text = response_content["choices"][0]["text"].strip()
        print(f"Generated Questions/Data Points for '{meeting_type}': {generated_text}")
        # Parse the generated text into actionable items/questions
        questions = generated_text.split('\n')
        return questions
    except Exception as e:
        print(f"Failed to generate meeting questions: {e}")
        return []