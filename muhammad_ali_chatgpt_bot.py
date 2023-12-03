import openai
import os
from dotenv import load_dotenv
import re
import spacy
from spacy.matcher import Matcher

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Function to classify the user's utterance using the first API call
def classify_user_input(utterance):
    #Our classification_prompt hopefully is specific enough so that MOST of the time it will only give us back THREE responses as we asked for that specifically.
    classification_prompt = f"Is the following utterance related to Muhammad Ali? (Follow this format as a response if it's not related to Muhammad Ali at all give back: 'No' if it's directly a question about Muhammad Ali give back: 'Yes' and it's a question that MAY be related to Muhammad Ali such as a question about his opponents then give back a response saying: 'Maybe'. I only ever want those three responses as responses.'{utterance}'?"
    classification_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=classification_prompt,
        temperature=0.7,
        max_tokens=50
    )

    #Use extract_category to check our api's response found in classification_response['choices'][0]['text'] and return an appropriate response to see if it relates to Muhammad Ali, doesn't or maybe (not directly about Muhammad Ali but still related)
    classified_category = extract_category(classification_response['choices'][0]['text'])
    return classified_category


# Function to generate a response based on the classified category using the second API call
def generate_response(classified_category, user_utterance):
    if classified_category == "Muhammad Ali":
        response_prompt = f"Generate a response to the user's inquiry about Muhammad Ali. User's utterance: '{user_utterance}'."
    elif classified_category == "Maybe related":
        response_prompt = f"The user's utterance is most likely about someone related to Muhammad Ali, give back an appropriate response on information that relates to their relationship with Muhammad Ali. User's utterance: '{user_utterance}'"
    else:
        response_prompt = f"Generate an appropriate response to the user's {classified_category} utterance making sure to let them know that this is a bot about Muhammad Ali. User's utterance: '{user_utterance}'."
    
    response_generation_response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=response_prompt,
        temperature=0.8,
        max_tokens=150
    )

    return response_generation_response['choices'][0]['text']

# Function to extract the category from the classification API response
def extract_category(api_response):
    print("This is api_response")
    print(api_response)
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

    try:
        while True:
            # Get user's input and process it
            utterance = input(">>> ").strip().lower().replace(".", "").replace("?", "")



            # Classify user input using the first API call
            classified_category = classify_user_input(utterance)
            
            # Generate a response based on the classified category using the second API call
            bot_response = generate_response(classified_category, utterance)
            
            print(bot_response)
    except KeyboardInterrupt:
        print("Goodbye!")

if __name__ == "__main__":
    # Run the main program
    main()
