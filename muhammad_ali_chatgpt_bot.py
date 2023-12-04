import openai
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to classify the user's utterance using the Completion API call from OpenAI
def classify_user_input(utterance):
    # Create a prompt 
    classification_prompt = f"Is the following utterance related to Muhammad Ali? (Follow this format as a response if it's not related to Muhammad Ali at all give back: 'No' if it's directly a question about Muhammad Ali give back: 'Yes' and it's a question that MAY be related to Muhammad Ali such as a question about his opponents then give back a response saying: 'Maybe'. I only ever want those three responses as responses.'{utterance}'?"
    #Do the API Call, giving it the prompt we just created
    classification_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=classification_prompt,
        temperature=0.7,
        max_tokens=50
    )
    #Utilize extract_category to give us back "Not related", "Maybe related" or "Muhammad Ali"
    classified_category = extract_category(classification_response['choices'][0]['text'])
    return classified_category

# Function to generate a response based on the classified category using the Chat API
def generate_response(classified_category, user_utterance, conversation_history):
    # Build the conversation input for the Chat API
    chat_input = [{'role': 'system', 'content': 'You are a knowledgeable assistant specializing in all things Muhammad Ali. Provide helpful and accurate information based on user inquiries and provide responses limited to 250 tokens.'}]    

    # Add both user and assistant messages to conversation history
    for i, utterance in enumerate(conversation_history):
        role = 'user' if i % 2 == 0 else 'assistant'
        chat_input.append({'role': role, 'content': utterance})

    # Append the current message to chat_input with additional context depending on what classified_category is so we can get back relevant responses
    if classified_category == "Muhammad Ali":
        chat_input.append({'role': 'user', 'content': user_utterance + " Generate a response to the user's inquiry about Muhammad Ali."})
    elif classified_category == "Maybe related":
        chat_input.append({'role': 'user', 'content': user_utterance + " The user's utterance is most likely about someone related to Muhammad Ali, give back an appropriate response on information that relates to their relationship with Muhammad Ali."})
    else:
        chat_input.append({'role': 'user', 'content': user_utterance + f" Generate an appropriate response to the user's {classified_category} utterance making sure to let them know that this is a bot about Muhammad Ali."})


    # Call the Chat API giving it chat_input
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_input,
        temperature=0.8,
        max_tokens=250
    )

    # Extract the assistant's reply and add it to conversation history
    assistant_reply = response['choices'][0]['message']['content']
    conversation_history.append(user_utterance)  # Add the user's message to conversation history
    conversation_history.append(assistant_reply)  # Add the assistant's reply to conversation history

    return assistant_reply

# Function to extract the category from the classification API response
def extract_category(api_response):
    # Check if the response matches the expected format
    if "No" in api_response or "No." in api_response:
        return "Not related"
    elif "Yes" in api_response or "Yes." in api_response:
        return "Muhammad Ali"
    elif "Maybe" in api_response or "Maybe." in api_response:
        return "Maybe related"
    else:
        return "unknown"

# Main program execution
def main():
    print("Hello! I know stuff about Muhammad Ali. When you're done, just say 'goodbye.'")

    conversation_history = []  # Initialize conversation history

    try:
        while True:
            # Get user's input and process it
            utterance = input(">>> ").strip().lower().replace(".", "").replace("?", "")

            # Classify user input using the first API call
            classified_category = classify_user_input(utterance)
            
            # Generate a response based on the classified category using the second API call
            bot_response = generate_response(classified_category, utterance, conversation_history)
            
            print(bot_response)
    except KeyboardInterrupt:
        print("Goodbye!")

if __name__ == "__main__":
    # Run the main program
    main()
