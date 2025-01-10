# import google.generativeai as genai
# import re
# from dotenv import load_dotenv
# import os
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# from googletrans import Translator

# # Load environment variables from .env (contains API keys, etc.)
# load_dotenv()

# # Initialize sentiment analyzer for user input sentiment scoring
# analyzer = SentimentIntensityAnalyzer()

# # Initialize translator for multi-language support
# translator = Translator(service_urls=['translate.google.com'])

# class CandidateChatbot:
#     """
#     A conversational chatbot that:
#       1. Collects a candidate's personal details (name, email, phone, etc.).
#       2. Conducts sentiment analysis on user inputs.
#       3. Allows the user to provide their tech stack and generates relevant technical questions.
#       4. Supports multiple languages by detecting user-provided language or using a default (English).
#       5. Utilizes the Google Generative AI (Gemini-Pro) model to generate questions.
#     """

#     def __init__(self):
#         """
#         Initialize the chatbot by:
#           - Loading an API key from environment variables.
#           - Configuring the generative AI model.
#           - Preparing placeholders for user details, tech stack, and questions.
#           - Setting the conversation state.
#         """

#         # Load the API key from the .env file
#         api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
#         if not api_key:
#             raise ValueError("API key is missing. Please set GOOGLE_GENAI_API_KEY in your .env file.")

#         # Configure the generative AI with the provided API key
#         genai.configure(api_key=api_key)

#         # Use the gemini-pro model (adjust if you have another model name)
#         self.model = genai.GenerativeModel('gemini-pro')

#         # The required user details (in order)
#         self.required_details = ["name", "email", "phone", "experience", "position", "location"]
#         self.current_index = 0  # To track which detail we are currently collecting
#         self.user_details = {}  # Store user-provided details

#         # Store tech stack in lowercase form, to handle repeated or case-insensitive input
#         self.tech_stack = []

#         # Dictionary to store questions, keyed by lowercase tech name
#         self.questions = {}

#         # Initial conversation state
#         self.state = "selecting_language"

#         # Executor for handling any synchronous tasks that might block (if needed)
#         self.executor = ThreadPoolExecutor()

#         # Default to English if no language is explicitly selected by the user
#         self.detected_lang = "en"

#     async def select_language(self):
#         """
#         Prompt user to select a language code (e.g., 'en', 'es'), returning the prompt message.
#         """
#         return "Please select your preferred language (default is English). For example, type 'en' for English, 'es' for Spanish, etc.:"

#     async def greet(self):
#         """
#         Change state to 'collecting_details' and return a greeting asking for the user's name.
#         """
#         self.state = "collecting_details"
#         return "What is your name?"

#     async def get_next_detail_prompt(self):
#         """
#         Return the next detail prompt (e.g., 'What is your email address?') based on `self.current_index`.
#         If we've collected all required details, switch to 'confirming_details' and call confirm_details().
#         """
#         if self.current_index < len(self.required_details):
#             detail = self.required_details[self.current_index]
#             prompts = {
#                 "name": "What is your name?",
#                 "email": "What is your email address?",
#                 "phone": "What is your phone number? (e.g., +1 9080706050)",
#                 "experience": "How many years of experience do you have?",
#                 "position": "What is your desired position?",
#                 "location": "Where are you currently located?"
#             }
#             return prompts.get(detail, "Please provide the required detail.")
#         else:
#             # We have all details; confirm them
#             self.state = "confirming_details"
#             return await self.confirm_details()

#     async def validate_input(self, field, value):
#         """
#         Validate user input for a specific field (name, email, phone, experience, position, location).
#         Returns True if valid, False otherwise.
#         """
#         value = value.strip()
#         if field == "name":
#             pattern = r'^[A-Za-z]+(?:[\'-]?[A-Za-z]+)*(?:\s[A-Za-z]+(?:[\'-]?[A-Za-z]+)*)*$'
#             return re.match(pattern, value) is not None
#         elif field == "email":
#             pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#             return re.match(pattern, value) is not None
#         elif field == "phone":
#             pattern = r'^\+\d+\s\d{10}$'
#             return re.match(pattern, value) is not None
#         elif field == "experience":
#             return value.isdigit() and int(value) > 0
#         elif field in ("position", "location"):
#             return len(value) > 0
#         else:
#             # For any unrecognized field, skip validation
#             return True

#     async def confirm_details(self):
#         """
#         Summarize the collected user details and ask the user for confirmation (yes/no).
#         Switch the state to 'confirming_details'.
#         """
#         details_display = f"Hello {self.user_details['name']}\n\n"
#         for key, value in self.user_details.items():
#             details_display += f"- {key.capitalize()}: {value}\n"
#         details_display += "\nAre these details correct? (yes/no)"
#         self.state = "confirming_details"
#         return details_display

#     def format_response(self, text, sentiment):
#         """
#         Format the chatbot's response by prepending the sentiment on a separate line,
#         followed by the response text.

#         e.g.,
#         Sentiment: Positive

#         Hello, this is the text!
#         """
#         # If not English, translate the text before final formatting
#         if self.detected_lang != 'en':
#             text = translator.translate(text, dest=self.detected_lang).text

#         # Return sentiment followed by two line breaks, then the text
#         return f"Sentiment: {sentiment.capitalize()}\n\n{text}"

#     async def handle_input(self, user_input):
#         """
#         Main entry point for handling user input. This manages the conversation state,
#         sentiment analysis, validation of details, tech-stack collection, and question generation.
#         Returns the formatted chatbot response with sentiment.
#         """
#         user_input = user_input.strip()

#         # 1) Language selection state
#         if self.state == "selecting_language":
#             # If user types 'en', 'es', etc., set that as detected_lang; otherwise default to 'en'
#             if user_input in translator.service_urls:
#                 self.detected_lang = user_input
#             else:
#                 self.detected_lang = "en"
#             self.state = "greeting"
#             return await self.greet()

#         # If we just greeted, switch to collecting details
#         if self.state == "greeting":
#             self.state = "collecting_details"

#         # 2) Translate user input to English for sentiment analysis (if necessary)
#         if self.detected_lang != 'en':
#             translated_input = translator.translate(user_input, dest='en').text
#         else:
#             translated_input = user_input

#         # 3) Perform sentiment analysis on the English version of user input
#         sentiment_score = analyzer.polarity_scores(translated_input)['compound']
#         if sentiment_score >= 0.05:
#             sentiment = "positive"
#         elif sentiment_score > -0.05:
#             sentiment = "neutral"
#         else:
#             sentiment = "negative"

#         # 4) Handle the conversation flow based on current state
#         if self.state == "collecting_details":
#             # Collecting user details (name, email, phone, experience, position, location)
#             if self.current_index < len(self.required_details):
#                 detail = self.required_details[self.current_index]
#                 # Validate the current detail
#                 if await self.validate_input(detail, translated_input):
#                     self.user_details[detail] = translated_input
#                     self.current_index += 1

#                     # If more details left, ask next detail
#                     if self.current_index < len(self.required_details):
#                         next_prompt = await self.get_next_detail_prompt()
#                         return self.format_response(next_prompt, sentiment)
#                     else:
#                         # If all details have been collected, confirm them
#                         confirm_msg = await self.confirm_details()
#                         return self.format_response(confirm_msg, sentiment)
#                 else:
#                     # Re-ask if validation failed
#                     error_msg = f"Invalid {detail}. Please re-enter."
#                     return self.format_response(error_msg, sentiment)
#             else:
#                 # If we somehow got here but have all details, confirm them
#                 confirm_msg = await self.confirm_details()
#                 return self.format_response(confirm_msg, sentiment)

#         elif self.state == "confirming_details":
#             # Confirming the user's details (yes/no)
#             if translated_input.lower() == "yes":
#                 self.state = "collecting_tech_stack"
#                 msg = "Great! Please provide your tech stack (e.g., Python, SQL, DL)."
#                 return self.format_response(msg, sentiment)
#             elif translated_input.lower() == "no":
#                 self.state = "editing_details"
#                 msg = "Which detail would you like to update? (e.g., name, email, phone, etc.)"
#                 return self.format_response(msg, sentiment)
#             else:
#                 msg = "Please respond with 'yes' or 'no'."
#                 return self.format_response(msg, sentiment)

#         elif self.state == "editing_details":
#             # User wants to update a specific detail
#             field = translated_input.lower()
#             if field in self.required_details:
#                 # e.g. if user says "name", we go to updating_name
#                 self.state = f"updating_{field}"
#                 return self.format_response(f"Please enter the correct {field}:", sentiment)
#             else:
#                 msg = "Invalid field. Please specify a valid detail to update."
#                 return self.format_response(msg, sentiment)

#         elif self.state.startswith("updating_"):
#             # After user indicates which detail to edit, they provide the new value
#             field = self.state.split("_")[1]
#             if await self.validate_input(field, translated_input):
#                 # Update the user detail and return to confirm
#                 self.user_details[field] = translated_input
#                 self.state = "confirming_details"
#                 confirm_msg = await self.confirm_details()
#                 return self.format_response(confirm_msg, sentiment)
#             else:
#                 error_msg = f"Invalid {field}. Please re-enter."
#                 return self.format_response(error_msg, sentiment)

#         elif self.state == "collecting_tech_stack":
#             # Collect the user's tech stack, normalize it to lowercase, and remove duplicates
#             self.tech_stack = list(
#                 set(tech.strip().lower() for tech in translated_input.split(","))
#             )

#             # Generate questions for the provided techs
#             await self.generate_questions(self.tech_stack)
#             self.state = "follow_up"

#             follow_up_msg = await self.display_questions_with_follow_up()
#             return self.format_response(follow_up_msg, sentiment)

#         elif self.state == "follow_up":
#             # After generating questions, check for user requests for more questions or ending
#             lower_input = translated_input.lower()

#             if lower_input in ["no", "bye", "goodbye"]:
#                 # End the conversation
#                 self.state = "ending_conversation"
#                 end_msg = self.end_conversation()
#                 return self.format_response(end_msg, sentiment)

#             elif lower_input.startswith(("questions on", "additional questions on", "more questions on")):
#                 # The user wants more questions on certain tech(s)
#                 techs = lower_input.replace("additional questions on", "") \
#                                    .replace("more questions on", "") \
#                                    .replace("questions on", "") \
#                                    .strip()
#                 tech_list = [t.strip().lower() for t in techs.split(",")]

#                 # Identify existing vs. new tech
#                 existing_techs = [t for t in tech_list if t in self.tech_stack]
#                 new_techs = [t for t in tech_list if t not in self.tech_stack]

#                 response = ""
#                 # If we have existing techs, generate *additional* questions
#                 if existing_techs:
#                     response += await self.generate_additional_questions_for_specific_techs(existing_techs)

#                 # If we have new techs, generate brand-new questions
#                 if new_techs:
#                     response += await self.generate_questions_for_new_tech(new_techs)

#                 # If user specified some techs but none match, show a helpful message
#                 if not response:
#                     response = (f"I couldn't find any valid tech stack from your request. "
#                                 f"Please try again with a valid tech from: {', '.join(self.tech_stack)}.")

#                 return self.format_response(response, sentiment)

#             elif lower_input == "yes":
#                 # If user says "yes", they might want to continue chatting or ask something else
#                 msg = "What else can I assist you with?"
#                 return self.format_response(msg, sentiment)
#             else:
#                 msg = "I didn't understand that. Please clarify your request or say 'bye' to end the conversation."
#                 return self.format_response(msg, sentiment)

#         elif self.state == "ending_conversation":
#             # Conversation is already ending
#             end_msg = self.end_conversation()
#             return self.format_response(end_msg, sentiment)

#         else:
#             # Catch-all for unexpected states
#             msg = "I didn't understand that. Please try again."
#             return self.format_response(msg, sentiment)

#     async def generate_questions(self, techs):
#         """
#         Generate initial questions for a list of techs and store them in `self.questions`.
        
#         :param techs: A list of lowercase tech stack items (e.g., ['python', 'sql']).
#         """
#         for tech in techs:
#             prompt = f"Generate 3-5 technical questions for {tech}."
#             response = self.model.generate_content(prompt)
#             self.questions[tech] = response.text  # Keyed by lowercase tech name

#     async def generate_additional_questions_for_specific_techs(self, tech_list):
#         """
#         Generate additional questions (3) for each existing tech in `tech_list`.
        
#         :param tech_list: List of existing tech items for which we want *additional* questions.
#         :return: A string containing the formatted additional questions.
#         """
#         response = "### Additional Questions for Existing Techs:\n"
#         for tech in tech_list:
#             prompt = f"Generate 3 additional technical questions for {tech}."
#             result = self.model.generate_content(prompt)
#             response += f"\n#### {tech.capitalize()}:\n{result.text}\n"
#         response += "\n\nIs there anything else you need, or do you want to say bye or goodbye?"
#         return response

#     async def generate_questions_for_new_tech(self, new_techs):
#         """
#         Generate brand-new questions for techs not yet in `self.tech_stack`. 
#         Add them to the tech stack and store the generated questions.
        
#         :param new_techs: List of new tech items (lowercase) to add to `self.tech_stack`.
#         :return: A string containing the formatted questions for new techs.
#         """
#         response = "\n\n### Questions for New Techs:\n"
#         for tech in new_techs:
#             prompt = f"Generate 3-5 technical questions for {tech}."
#             result = self.model.generate_content(prompt)

#             # Add to tech stack
#             self.tech_stack.append(tech)

#             # Store questions keyed by lowercase
#             self.questions[tech] = result.text
#             response += f"\n#### {tech.capitalize()}:\n{result.text}\n"

#         response += (
#             "\n\nI've updated your tech stack. Is there anything else you need, "
#             "or do you want to say bye or goodbye?"
#         )
#         return response

#     async def display_questions_with_follow_up(self):
#         """
#         Display the already-generated questions for each tech in `self.questions`.
#         Then prompt if there's anything else needed.
        
#         :return: A string containing the formatted list of generated questions for each tech.
#         """
#         questions_display = "### Generated Questions:\n"
#         for tech, qs in self.questions.items():
#             # tech is lowercase, so we can capitalize for nicer display
#             questions_display += f"\n#### {tech.capitalize()}:\n{qs}\n"

#         questions_display += (
#             "\n\nIs there anything else you need (yes/no), or do you want to say bye or goodbye?"
#         )
#         return questions_display

#     def end_conversation(self):
#         """
#         Return a closing farewell message, indicating the end of the conversation.
        
#         :return: A string with a thank-you note and polite closing.
#         """
#         farewell = (
#             "Thank you for your time! We will review your information and get back to you shortly.\n"
#             "Have a great day!"
#         )
#         return farewell


#=============================================================================================================

import google.generativeai as genai
import re
from dotenv import load_dotenv
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator

# Load environment variables from .env (contains API keys, etc.)
load_dotenv()

# Initialize sentiment analyzer for user input sentiment scoring
analyzer = SentimentIntensityAnalyzer()

# Initialize translator for multi-language support
translator = Translator(service_urls=['translate.google.com'])

class CandidateChatbot:
    """
    A conversational chatbot that:
      1. Collects a candidate's personal details (name, email, phone, etc.).
      2. Conducts sentiment analysis on user inputs.
      3. Allows the user to provide their tech stack and generates relevant technical questions.
      4. Supports multiple languages by detecting user-provided language or using a default (English).
      5. Utilizes the Google Generative AI (Gemini-Pro) model to generate questions.
    """

    def __init__(self):
        """
        Initialize the chatbot by:
          - Loading an API key from environment variables.
          - Configuring the generative AI model.
          - Preparing placeholders for user details, tech stack, and questions.
          - Setting the conversation state.
        """

        # Load the API key from the .env file
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key is missing. Please set GOOGLE_GENAI_API_KEY in your .env file.")

        # Configure the generative AI with the provided API key
        genai.configure(api_key=api_key)

        # Use the gemini-pro model (adjust if you have another model name)
        self.model = genai.GenerativeModel('gemini-pro')

        # The required user details (in order)
        self.required_details = ["name", "email", "phone", "experience", "position", "location"]
        self.current_index = 0  # To track which detail we are currently collecting
        self.user_details = {}  # Store user-provided details

        # Store tech stack in lowercase form, to handle repeated or case-insensitive input
        self.tech_stack = []

        # Dictionary to store questions, keyed by lowercase tech name
        self.questions = {}

        # Initial conversation state
        self.state = "selecting_language"

        # Executor for handling any synchronous tasks that might block (if needed)
        self.executor = ThreadPoolExecutor()

        # Default to English if no language is explicitly selected by the user
        self.detected_lang = "en"

        # Simulated data storage (in-memory, anonymized)
        self.simulated_data = {
            "candidates": [],  # Store anonymized candidate data
            "technical_responses": []  # Store technical responses (anonymized)
        }

    async def select_language(self):
        """
        Prompt user to select a language code (e.g., 'en', 'es'), returning the prompt message.
        """
        return "Please select your preferred language (default is English). For example, type 'en' for English, 'es' for Spanish, etc.:"

    async def greet(self):
        """
        Change state to 'collecting_details' and return a greeting asking for the user's name.
        """
        self.state = "collecting_details"
        return "What is your name?"

    async def get_next_detail_prompt(self):
        """
        Return the next detail prompt (e.g., 'What is your email address?') based on `self.current_index`.
        If we've collected all required details, switch to 'confirming_details' and call confirm_details().
        """
        if self.current_index < len(self.required_details):
            detail = self.required_details[self.current_index]
            prompts = {
                "name": "What is your name?",
                "email": "What is your email address?",
                "phone": "What is your phone number? (e.g., +1 9080706050)",
                "experience": "How many years of experience do you have?",
                "position": "What is your desired position?",
                "location": "Where are you currently located?"
            }
            return prompts.get(detail, "Please provide the required detail.")
        else:
            # We have all details; confirm them
            self.state = "confirming_details"
            return await self.confirm_details()

    async def validate_input(self, field, value):
        """
        Validate user input for a specific field (name, email, phone, experience, position, location).
        Returns True if valid, False otherwise.
        """
        value = value.strip()
        if field == "name":
            pattern = r'^[A-Za-z]+(?:[\'-]?[A-Za-z]+)*(?:\s[A-Za-z]+(?:[\'-]?[A-Za-z]+)*)*$'
            return re.match(pattern, value) is not None
        elif field == "email":
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, value) is not None
        elif field == "phone":
            pattern = r'^\+\d+\s\d{10}$'
            return re.match(pattern, value) is not None
        elif field == "experience":
            return value.isdigit() and int(value) > 0
        elif field in ("position", "location"):
            return len(value) > 0
        else:
            # For any unrecognized field, skip validation
            return True

    async def confirm_details(self):
        """
        Summarize the collected user details and ask the user for confirmation (yes/no).
        Switch the state to 'confirming_details'.
        """
        details_display = f"Hello {self.user_details['name']}\n\n"
        for key, value in self.user_details.items():
            details_display += f"- {key.capitalize()}: {value}\n"
        details_display += "\nAre these details correct? (yes/no)"
        self.state = "confirming_details"
        return details_display

    def format_response(self, text, sentiment):
        """
        Format the chatbot's response by prepending the sentiment on a separate line,
        followed by the response text.

        e.g.,
        Sentiment: Positive

        Hello, this is the text!
        """
        # If not English, translate the text before final formatting
        if self.detected_lang != 'en':
            text = translator.translate(text, dest=self.detected_lang).text

        # Return sentiment followed by two line breaks, then the text
        return f"Sentiment: {sentiment.capitalize()}\n\n{text}"

    async def handle_input(self, user_input):
        """
        Main entry point for handling user input. This manages the conversation state,
        sentiment analysis, validation of details, tech-stack collection, and question generation.
        Returns the formatted chatbot response with sentiment.
        """
        user_input = user_input.strip()

        # 1) Language selection state
        if self.state == "selecting_language":
            # If user types 'en', 'es', etc., set that as detected_lang; otherwise default to 'en'
            if user_input in translator.service_urls:
                self.detected_lang = user_input
            else:
                self.detected_lang = "en"
            self.state = "greeting"
            return await self.greet()

        # If we just greeted, switch to collecting details
        if self.state == "greeting":
            self.state = "collecting_details"

        # 2) Translate user input to English for sentiment analysis (if necessary)
        if self.detected_lang != 'en':
            translated_input = translator.translate(user_input, dest='en').text
        else:
            translated_input = user_input

        # 3) Perform sentiment analysis on the English version of user input
        sentiment_score = analyzer.polarity_scores(translated_input)['compound']
        if sentiment_score >= 0.05:
            sentiment = "positive"
        elif sentiment_score > -0.05:
            sentiment = "neutral"
        else:
            sentiment = "negative"

        # 4) Handle the conversation flow based on current state
        if self.state == "collecting_details":
            # Collecting user details (name, email, phone, experience, position, location)
            if self.current_index < len(self.required_details):
                detail = self.required_details[self.current_index]
                # Validate the current detail
                if await self.validate_input(detail, translated_input):
                    self.user_details[detail] = translated_input
                    self.current_index += 1

                    # If more details left, ask next detail
                    if self.current_index < len(self.required_details):
                        next_prompt = await self.get_next_detail_prompt()
                        return self.format_response(next_prompt, sentiment)
                    else:
                        # If all details have been collected, confirm them
                        confirm_msg = await self.confirm_details()
                        return self.format_response(confirm_msg, sentiment)
                else:
                    # Re-ask if validation failed
                    error_msg = f"Invalid {detail}. Please re-enter."
                    return self.format_response(error_msg, sentiment)
            else:
                # If we somehow got here but have all details, confirm them
                confirm_msg = await self.confirm_details()
                return self.format_response(confirm_msg, sentiment)

        elif self.state == "confirming_details":
            # Confirming the user's details (yes/no)
            if translated_input.lower() == "yes":
                self.state = "collecting_tech_stack"
                msg = "Great! Please provide your tech stack (e.g., Python, SQL, DL)."
                return self.format_response(msg, sentiment)
            elif translated_input.lower() == "no":
                self.state = "editing_details"
                msg = "Which detail would you like to update? (e.g., name, email, phone, etc.)"
                return self.format_response(msg, sentiment)
            else:
                msg = "Please respond with 'yes' or 'no'."
                return self.format_response(msg, sentiment)

        elif self.state == "editing_details":
            # User wants to update a specific detail
            field = translated_input.lower()
            if field in self.required_details:
                # e.g. if user says "name", we go to updating_name
                self.state = f"updating_{field}"
                return self.format_response(f"Please enter the correct {field}:", sentiment)
            else:
                msg = "Invalid field. Please specify a valid detail to update."
                return self.format_response(msg, sentiment)

        elif self.state.startswith("updating_"):
            # After user indicates which detail to edit, they provide the new value
            field = self.state.split("_")[1]
            if await self.validate_input(field, translated_input):
                # Update the user detail and return to confirm
                self.user_details[field] = translated_input
                self.state = "confirming_details"
                confirm_msg = await self.confirm_details()
                return self.format_response(confirm_msg, sentiment)
            else:
                error_msg = f"Invalid {field}. Please re-enter."
                return self.format_response(error_msg, sentiment)

        elif self.state == "collecting_tech_stack":
            # Collect the user's tech stack, normalize it to lowercase, and remove duplicates
            self.tech_stack = list(
                set(tech.strip().lower() for tech in translated_input.split(","))
            )

            # Generate questions for the provided techs
            await self.generate_questions(self.tech_stack)
            self.state = "follow_up"

            follow_up_msg = await self.display_questions_with_follow_up()
            return self.format_response(follow_up_msg, sentiment)

        elif self.state == "follow_up":
            # After generating questions, check for user requests for more questions or ending
            lower_input = translated_input.lower()

            if lower_input in ["no", "bye", "goodbye"]:
                # End the conversation
                self.state = "ending_conversation"
                end_msg = await self.end_conversation()  # Await the coroutine
                return self.format_response(end_msg, sentiment)

            elif lower_input.startswith(("questions on", "additional questions on", "more questions on")):
                # The user wants more questions on certain tech(s)
                techs = lower_input.replace("additional questions on", "") \
                                   .replace("more questions on", "") \
                                   .replace("questions on", "") \
                                   .strip()
                tech_list = [t.strip().lower() for t in techs.split(",")]

                # Identify existing vs. new tech
                existing_techs = [t for t in tech_list if t in self.tech_stack]
                new_techs = [t for t in tech_list if t not in self.tech_stack]

                response = ""
                # If we have existing techs, generate *additional* questions
                if existing_techs:
                    response += await self.generate_additional_questions_for_specific_techs(existing_techs)

                # If we have new techs, generate brand-new questions
                if new_techs:
                    response += await self.generate_questions_for_new_tech(new_techs)

                # If user specified some techs but none match, show a helpful message
                if not response:
                    response = (f"I couldn't find any valid tech stack from your request. "
                                f"Please try again with a valid tech from: {', '.join(self.tech_stack)}.")

                return self.format_response(response, sentiment)

            elif lower_input == "yes":
                # If user says "yes", they might want to continue chatting or ask something else
                msg = "What else can I assist you with?"
                return self.format_response(msg, sentiment)
            else:
                msg = "I didn't understand that. Please clarify your request or say 'bye' to end the conversation."
                return self.format_response(msg, sentiment)

        elif self.state == "ending_conversation":
            # Conversation is already ending
            end_msg = await self.end_conversation()  # Await the coroutine
            return self.format_response(end_msg, sentiment)

        else:
            # Catch-all for unexpected states
            msg = "I didn't understand that. Please try again."
            return self.format_response(msg, sentiment)
        
    async def anonymize_data(self, data):
        """
        Anonymize user data by removing or obfuscating personally identifiable information (PII).
        """
        anonymized_data = {
            "name": "Anonymous",
            "email": "anonymous@example.com",
            "phone": "000-000-0000",
            "experience": data.get("experience", "0"),
            "position": data.get("position", "Unknown"),
            "location": data.get("location", "Unknown"),
            "tech_stack": data.get("tech_stack", []),
            "questions": data.get("questions", {})
        }
        return anonymized_data

    async def store_simulated_data(self):
        """
        Store anonymized candidate data and technical responses in simulated data storage.
        """
        anonymized_data = await self.anonymize_data({
            **self.user_details,
            "tech_stack": self.tech_stack,
            "questions": self.questions
        })
        self.simulated_data["candidates"].append(anonymized_data)
        self.simulated_data["technical_responses"].append({
            "tech_stack": self.tech_stack,
            "questions": self.questions
        })

    async def generate_questions(self, techs):
        """
        Generate initial questions for a list of techs and store them in `self.questions`.
        
        :param techs: A list of lowercase tech stack items (e.g., ['python', 'sql']).
        """
        for tech in techs:
            prompt = f"Generate 3-5 technical questions for {tech}."
            response = self.model.generate_content(prompt)
            self.questions[tech] = response.text  # Keyed by lowercase tech name

    async def generate_additional_questions_for_specific_techs(self, tech_list):
        """
        Generate additional questions (3) for each existing tech in `tech_list`.
        
        :param tech_list: List of existing tech items for which we want *additional* questions.
        :return: A string containing the formatted additional questions.
        """
        response = "### Additional Questions for Existing Techs:\n"
        for tech in tech_list:
            prompt = f"Generate 3 additional technical questions for {tech}."
            result = self.model.generate_content(prompt)
            response += f"\n#### {tech.capitalize()}:\n{result.text}\n"
        response += "\n\nIs there anything else you need, or do you want to say bye or goodbye?"
        return response

    async def generate_questions_for_new_tech(self, new_techs):
        """
        Generate brand-new questions for techs not yet in `self.tech_stack`. 
        Add them to the tech stack and store the generated questions.
        
        :param new_techs: List of new tech items (lowercase) to add to `self.tech_stack`.
        :return: A string containing the formatted questions for new techs.
        """
        response = "\n\n### Questions for New Techs:\n"
        for tech in new_techs:
            prompt = f"Generate 3-5 technical questions for {tech}."
            result = self.model.generate_content(prompt)

            # Add to tech stack
            self.tech_stack.append(tech)

            # Store questions keyed by lowercase
            self.questions[tech] = result.text
            response += f"\n#### {tech.capitalize()}:\n{result.text}\n"

        response += (
            "\n\nI've updated your tech stack. Is there anything else you need, "
            "or do you want to say bye or goodbye?"
        )
        return response

    async def display_questions_with_follow_up(self):
        """
        Display the already-generated questions for each tech in `self.questions`.
        Then prompt if there's anything else needed.
        
        :return: A string containing the formatted list of generated questions for each tech.
        """
        questions_display = "### Generated Questions:\n"
        for tech, qs in self.questions.items():
            # tech is lowercase, so we can capitalize for nicer display
            questions_display += f"\n#### {tech.capitalize()}:\n{qs}\n"

        questions_display += (
            "\n\nIs there anything else you need (yes/no), or do you want to say bye or goodbye?"
        )
        return questions_display

    async def end_conversation(self):
        """
        Return a closing farewell message, indicating the end of the conversation.
        
        :return: A string with a thank-you note and polite closing.
        """

        await self.store_simulated_data()  # Store anonymized data

        farewell = (
            "Thank you for your time! We will review your information and get back to you shortly.\n"
            "Have a great day!"
        )
        return farewell
