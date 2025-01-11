# Candidate Screening Chatbot

This repository contains a **Candidate Screening Chatbot** built with [Streamlit](https://streamlit.io/), [Google Generative AI (Gemini-Pro)](https://cloud.google.com/generative-ai/), and [googletrans](https://pypi.org/project/googletrans/) for translation. It allows a user (candidate) to enter personal information, select a preferred language, and answer job-related questions. The chatbot performs **sentiment analysis** on each user input and can **generate technical questions** based on the user’s chosen technology stack.

---

## Table of Contents
1. [Features](#features)  
2. [Installation and Setup](#installation-and-setup)  
3. [Environment Variables](#environment-variables)  
4. [How It Works](#how-it-works)  
    - [Streamlit App Flow](#streamlit-app-flow)  
    - [The `CandidateChatbot` Class](#the-candidatechatbot-class)  
    - [Conversation States](#conversation-states)  
5. [Code Walkthrough](#code-walkthrough)  
    - [Main Streamlit File](#main-streamlit-file)  
    - [CandidateChatbot Class File](#candidatechatbot-class-file)  
6. [Usage](#usage)  
7. [Docker Usage](#docker-usage)  
8. [Contributing](#contributing)  
9. [License](#license)  

---

## Features

- **Multi-language Support**: Users can select a preferred language (default is English) at the beginning. 
- **Conversation State Management**: The chatbot remembers past messages and user details using `st.session_state`.
- **Sentiment Analysis**: Each user input is analyzed by [VADER Sentiment Analysis](https://pypi.org/project/vaderSentiment/).
- **Dynamic Question Generation**: Technical questions are generated based on the user’s declared tech stack, using Google Generative AI (Gemini-Pro).
- **Detail Collection**: The chatbot collects user details such as name, email, phone number, years of experience, position, and location in a structured manner.
- **User Input Validation**: Some fields (like email, phone, etc.) are validated with regular expressions before proceeding.
- **Editing Collected Details**: The user can edit any previously provided detail if they made a mistake or want to update.
- **Language Translation**: The chatbot can automatically translate responses if a language other than English is chosen.

---

## Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Create a Virtual Environment (Optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add Environment Variables**  
   Create a `.env` file in the project root, including the required environment variables (see [Environment Variables](#environment-variables)).

5. **Run the Streamlit App**
   ```bash
   streamlit run <script_name>.py
   ```
   Replace `<script_name>.py` with the name of your main Streamlit file (for example, `app.py` or `main.py`).

---

## Environment Variables

You need a `.env` file to store sensitive information (like API keys). For instance:

```bash
# .env
GOOGLE_GEMINI_API_KEY=<your_google_gemini_pro_api_key_here>
```

This key is used by the Google Generative AI library (`google.generativeai`) to authenticate requests to the Gemini-Pro model.

---

## How It Works

### Streamlit App Flow

1. **Startup**: The application loads, and a custom CSS styling is applied to format the chat area.
2. **Session State Initialization**:
   - A `CandidateChatbot()` instance is stored in `st.session_state["chatbot"]`.
   - `messages` list is used to keep track of the conversation.
   - `language_selected` is a boolean that indicates whether the user’s language preference is set.
   - `selected_language` holds the user’s chosen language code (defaults to `"en"`).
   - `translator` is an instance of `Translator` from `googletrans`, used for any translations.
3. **Language Selection Phase**:
   - The user is asked to enter a language code (like `"en"` for English, `"es"` for Spanish, etc.).
   - If a code is provided, it is stored, and the conversation moves forward. Otherwise, `en` is used.
4. **Main Chat Flow**:
   - User details are collected step by step (name, email, phone, etc.).
   - The chatbot confirms the details, then asks the user for their tech stack.
   - Technical questions are generated, displayed, and can be further customized or repeated.
   - The conversation ends when the user indicates they’re done.

### The `CandidateChatbot` Class

This class encapsulates the conversation logic, including:
- **State Management**: Each state (`selecting_language`, `collecting_details`, `confirming_details`, `collecting_tech_stack`, etc.) guides the conversation flow.
- **Sentiment Analysis**: Uses `vaderSentiment` to score each user input. The combined score is converted to a `'positive'`, `'neutral'`, or `'negative'` label.
- **Validation**: Ensures certain user-provided inputs (like email and phone) match specific patterns.
- **Translation**: Text is translated to/from English as needed via `googletrans`.
- **Technical Question Generation**: Interacts with `google.generativeai` (Gemini-Pro) to produce relevant questions for each tech stack item.

### Conversation States

1. **`selecting_language`**: Prompts the user to pick a language code.  
2. **`greeting`**: Sends a greeting after the language is set.  
3. **`collecting_details`**: Sequentially collects required user details (name, email, etc.).  
4. **`confirming_details`**: Presents the collected info to the user for confirmation.  
5. **`editing_details`**: If the user says details are incorrect, they can specify which to correct.  
6. **`updating_<detail>`**: The chatbot updates the specified detail (e.g., updating_name).  
7. **`collecting_tech_stack`**: Asks the user for their list of technologies.  
8. **`follow_up`**: Offers additional questions or ends the conversation.  
9. **`ending_conversation`**: Displays a farewell message.

---

## Code Walkthrough

Below is a high-level explanation of the two main sections: the Streamlit app code and the `CandidateChatbot` class.

### Main Streamlit File

1. **Library Imports**:
   ```python
   import streamlit as st
   import asyncio
   from chatbot import CandidateChatbot
   from googletrans import Translator
   ```
   - `streamlit` for building the UI.
   - `asyncio` for async function calls (especially generating questions).
   - `CandidateChatbot` is our main chatbot logic class (imported from `chatbot.py` or a similar file).
   - `Translator` from `googletrans` for translations.

2. **Optional Custom CSS**:
   ```python
   st.markdown(
       """
       <style>
       .chat-title {
           text-align: center;
           font-size: 2.5em;
           ...
       }
       </style>
       """,
       unsafe_allow_html=True,
   )
   ```
   - Adds custom styling to the chat title, subtitle, etc.

3. **Session State Initialization**:
   ```python
   if "chatbot" not in st.session_state:
       st.session_state["chatbot"] = CandidateChatbot()
       st.session_state["messages"] = []
       st.session_state["language_selected"] = False
       st.session_state["selected_language"] = "en"
       st.session_state["translator"] = Translator(service_urls=['translate.google.com'])
   ```
   - Ensures that the chatbot instance and other variables persist across re-runs in Streamlit.

4. **Language Selection Phase**:
   ```python
   if not st.session_state["language_selected"]:
       st.markdown("<div style='background-color: #ede7f6; ...'>Please select your preferred language...</div>", unsafe_allow_html=True)

       if user_input := st.chat_input("Type your language code here...", key="language_input"):
           # Store selected language or default to "en"
           ...
           st.rerun()
   ```
   - Asks the user for a language code. Once set, the code calls `st.rerun()` to restart the app flow.

5. **Main Chat Flow**:
   - **Display Previous Messages**:
     ```python
     for message in st.session_state["messages"]:
         with st.chat_message(message["role"]):
             st.write(message["content"])
     ```
     - Renders each stored chat message in the UI.
   - **Capture New User Input**:
     ```python
     if user_input := st.chat_input("Type your response here..."):
         st.session_state["messages"].append({"role": "user", "content": user_input})
         ...
     ```
     - When the user enters a new message, it’s appended to the `messages` list.

   - **Process User Input**:
     ```python
     response = asyncio.run(st.session_state["chatbot"].handle_input(user_input))
     ```
     - Uses `asyncio.run()` to handle the user input via the chatbot’s main logic function, `handle_input(...)`.
     - If a non-English language is selected, the response is translated back to that language.

   - **Display Chatbot Response**:
     ```python
     st.session_state["messages"].append({"role": "assistant", "content": response})
     with st.chat_message("assistant"):
         st.write(response)
     ```

### CandidateChatbot Class File

In a separate file (e.g., `chatbot.py`), we have:

1. **Imports**:
   ```python
   import google.generativeai as genai
   import re
   from dotenv import load_dotenv
   import os
   import asyncio
   from concurrent.futures import ThreadPoolExecutor
   from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
   from googletrans import Translator
   ```

2. **Global Initializations**:
   ```python
   load_dotenv()
   analyzer = SentimentIntensityAnalyzer()
   translator = Translator(service_urls=['translate.google.com'])
   ```

3. **`CandidateChatbot` Class**:
   ```python
   class CandidateChatbot:
       def __init__(self):
           ...
       async def handle_input(self, user_input):
           ...
       async def generate_questions(self, techs):
           ...
       # etc.
   ```
   - Manages conversation flow, user details, generating questions, and translations.

4. **Key Methods**:
   - **`__init__`**:
     - Configures `google.generativeai` with the API key from `.env`.
     - Prepares the list of required user details.
     - Sets up default state and placeholders.
   - **`handle_input(user_input)`**:
     - The core function called every time the user enters something new.
     - Uses the current `state` to decide what to do (collect details, confirm details, generate questions, etc.).
     - Applies VADER sentiment analysis to either the raw user input (if English) or its translated version (if non-English).
   - **`validate_input(field, value)`**:
     - Uses regex or simple checks to ensure data consistency (e.g., email format, phone format).
   - **`anonymize_data(self, data)`**:
     - Replaces personal info with generic placeholders for data privacy.
   - **`store_simulated_data(self)`**:
     - Stores the anonymized data in self.simulated_data to simulate saving data in a database.  
   - **`generate_questions(techs)`**:
     - Uses the Gemini-Pro model to create 3–5 questions for each technology in the user’s tech stack.
   - **State-Specific Helper Methods**:
     - `select_language()`, `greet()`, `get_next_detail_prompt()`, `confirm_details()`, `generate_additional_questions_for_specific_techs()`, etc.

---

## Usage

1. **Start the Streamlit App**  
   ```bash
   streamlit run app.py
   ```
   (Replace `app.py` with the file containing the Streamlit code.)

2. **Interact with the Chat**  
   - In your browser, go to the local URL (e.g., `http://localhost:8501`) that Streamlit provides.
   - You’ll be prompted to select a language code (e.g., `en`, `es`).
   - Provide your details (name, email, phone, etc.) in the chat.
   - Input your technology stack (e.g., `Python, SQL`).
   - The chatbot will generate technical questions.
   - Continue the conversation by asking for additional questions or saying `bye` to end.

3. **Check Logs / Debug**  
   - By default, Streamlit prints out logs in the terminal where you launched it.  
   - If something goes wrong, ensure your `.env` file is correct and that you have a valid Google Generative AI key.

---

## Docker Usage

If you prefer to run this application within a Docker container, you can use the following commands:

1. **Build the Docker image** (from the project’s root directory):
   ```bash
   docker build -t streamlit-chatbot .
   ```
   This command will create a Docker image called `streamlit-chatbot` using the instructions in your `Dockerfile`.

2. **Run the Docker container**:
   ```bash
   docker run -p 8501:8501 --env GOOGLE_GEMINI_API_KEY=%GEMINI_API_KEY% streamlit-chatbot
   ```
   - `-p 8501:8501` maps the container’s port 8501 to your local machine’s port 8501.
   - `--env GOOGLE_GEMINI_API_KEY=%GEMINI_API_KEY%` injects the required environment variable (make sure `%GEMINI_API_KEY%` is set on your system beforehand).
   - The container will start the Streamlit application, and you can access it at `http://localhost:8501`.

**Note for non-Windows users**: Replace `%GEMINI_API_KEY%` with `$GEMINI_API_KEY` or whichever format is supported by your shell (e.g., `export GEMINI_API_KEY=your_key_value` before running the `docker run` command).

---

## Contributing

Contributions are welcome! If you have suggestions or want to add features:
1. Fork the repository.
2. Create a new branch.
3. Make your changes and push them.
4. Create a Pull Request (PR).

---

## License

This project is distributed under the MIT License.  
See the [LICENSE](LICENSE) file for more details.
