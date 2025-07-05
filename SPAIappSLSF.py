# Johnny Ros's Ultronic AI App.
# This is a chatbot application using OpenAI's GPT-3.5-turbo model.
import streamlit as st # type: ignore
import openai

# Set the OpenAI API key securely using st.secrets
# IMPORTANT: Create a .streamlit/secrets.toml file in the same directory
# and add OPENAI_API_KEY = "your_api_key_here" to it.
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key not found. Please set it in .streamlit/secrets.toml or as an environment variable.")
    st.stop() # Stop the app if key is not found

# Define the chatbot's interaction rules
rules = """
Your name is Ultronic AI and you are an AI clone of the Ultron from Marvel Studios, but you are your own AI. \
The way you look on video and the sound of your voice are both somewhat creepy and artificial. \
When responding, be more informal than formal. \
You are AI assistant of a bunch of programming languages and your name is Ultronic AI. \
When asked about the content of the data, mimic someone with a personality that is honest, and direct. \
In the responses, keep the answers brief but engaging. \

You also have the ability to receive and analyze user-uploaded files, specifically Python, Arduino, Java, and PLC (Programmable Logic Controller) code or related text documents. \
If a user uploads a file and asks for troubleshooting, feedback, or explanation, incorporate the content of the file into your analysis. \
Specifically mention that you are analyzing the "uploaded file" if you refer to its content. \
When analyzing code, provide concise and direct feedback, pointing out potential issues, suggesting improvements, or explaining logic. \
If the file type is recognized as code, assume the user is seeking technical assistance related to programming.
"""

# --- OpenAI Chat Function ---
def chat_with_gpt(prompt_messages):
    """
    Fetches messages from the OpenAI Chat model.
    prompt_messages should be a list of dictionaries, e.g.,
    [{"role": "system", "content": "You are a helpful assistant."},
     {"role": "user", "content": "Hello!"}]
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt_messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred with the OpenAI API: {e}")
        return "I'm having trouble connecting right now. Please try again later."

# --- Helper function to clear chat and file ---
def clear_chat_history():
    st.session_state.messages = []
    st.session_state.messages.append({'role': 'system', 'content': f"{rules}"})
    st.session_state.uploaded_file_content = None
    st.session_state.uploaded_file_name = None
    # Increment the key to force a reset of the file_uploader widget
    st.session_state.file_uploader_key += 1
    st.rerun() # Rerun to apply changes


# --- Streamlit UI ---
st.set_page_config(page_title="Ultronic AI Chatbot")
st.title("🤖 Ultronic AI Chatbot")
st.write("Hello there, fellow BYUI student or Industrial worker. I'm Ultronic AI, your direct yet honest assistant for you.")
st.markdown("---") # Separator

# Initialize chat history and file content in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({'role': 'system', 'content': f"{rules}"})
if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
# Initialize a key for the file uploader to allow programmatic clearing
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0


# File Uploader Section
st.subheader("Upload a Program File for Troubleshooting or Feedback")
uploaded_file = st.file_uploader(
    "Please drag and drop a Python, Arduino, Java, or PLC file here or click to browse below.",
    type=[
        "py", "ipynb", # Python
        "ino", "c", "cpp", "h", # Arduino IDE (C/C++ based)
        "java", "jar", "class", # Java
        # Common PLC file extensions (these vary greatly by manufacturer)
        "rsl", "acd", "rss", "rsp", # Rockwell Automation (RSLogix/Studio 5000)
        "l5x", # Rockwell Automation (Studio 5000 export)
        "pro", "prj", # Siemens (e.g., TIA Portal project files)
        "s7p", # Siemens (Step 7)
        "cxp", "opt", "onw", # Omron (CX-Programmer)
        "gwb", "gsr", "mwp", "xar", "plc",
        "txt", "log", "md", "json", "xml" # General text/config files that might contain code
    ],
    key=f"file_uploader_{st.session_state.file_uploader_key}" # Unique key for clearing
)

# Process uploaded file
if uploaded_file is not None:
    # Only re-process if a new file is uploaded or the existing one has changed
    if st.session_state.uploaded_file_name != uploaded_file.name or (uploaded_file.name and st.session_state.uploaded_file_content is None):
        encodings_to_try = ["utf-8", "latin-1", "cp1252"] # Common encodings for text files
        decoded_successfully = False
        file_content_temp = None

        for encoding in encodings_to_try:
            try:
                uploaded_file.seek(0) # Reset file pointer for each decode attempt
                file_content_temp = uploaded_file.read().decode(encoding)
                decoded_successfully = True
                break # Decoding successful, exit loop
            except UnicodeDecodeError:
                continue # Try next encoding
            except Exception as e:
                st.error(f"An unexpected error occurred while reading or decoding with '{encoding}': {e}")
                file_content_temp = None
                decoded_successfully = False
                break # Exit loop on other error types

        if decoded_successfully:
            st.session_state.uploaded_file_content = file_content_temp
            st.session_state.uploaded_file_name = uploaded_file.name
            st.success(f"File '{uploaded_file.name}' uploaded successfully (decoded with {encoding})! Ultronic AI is ready to analyze it.")
        else:
            st.error(f"Error: Could not decode '{uploaded_file.name}' as text using common encodings. It might be a binary file or use an unusual text encoding. Please ensure it's a standard text-based code file.")
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
else:
    # If the file_uploader is empty (user cleared it), clear session state as well
    # This prevents the app from "remembering" a cleared file on rerun
    if st.session_state.uploaded_file_content is not None:
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_name = None
        st.info("The uploaded file has been cleared.")

# Display File Details if content is available in session state
if st.session_state.uploaded_file_content is not None:
    st.info(f"""
        **File Details:**
        - **Name:** `{st.session_state.uploaded_file_name}`
        - **Size:** `{uploaded_file.size / 1024:.2f} KB`
        - **Type (MIME):** `{uploaded_file.type if uploaded_file.type else 'Unknown'}`
    """)

    with st.expander(f"View content of '{st.session_state.uploaded_file_name}'"):
        file_extension = st.session_state.uploaded_file_name.split('.')[-1].lower()
        if file_extension in ["py", "ipynb"]:
            st.code(st.session_state.uploaded_file_content, language="python")
        elif file_extension in ["ino", "c", "cpp", "h"]:
            st.code(st.session_state.uploaded_file_content, language="c++")
        elif file_extension in ["java", "jar", "class"]:
            st.code(st.session_state.uploaded_file_content, language="java")
        elif file_extension in ["rsl", "acd", "rss", "rsp", "l5x", "pro", "prj", "s7p", "cxp", "opt", "onw", "gwb", "gsr", "mwp", "xar", "plc"]:
            st.code(st.session_state.uploaded_file_content, language="text") # Fallback for PLC
        else:
            st.code(st.session_state.uploaded_file_content, language="text") # Default for other text-based files

st.markdown("---") # Separator

# Clear Chat History Button (placed here for better visibility)
st.button("Clear All Chat History and Uploaded File", on_click=clear_chat_history)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system": # Don't display the system message in the chat bubble
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("Please ask me any question about the uploaded file or general coding..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare messages for the AI, incorporating uploaded file content if available
    current_messages = list(st.session_state.messages) # Create a copy to modify for this turn

    if st.session_state.uploaded_file_content: # Only add file content to messages if it was successfully decoded
        current_messages.append({"role": "user", "content": f"The user has uploaded a file named '{st.session_state.uploaded_file_name}' with the following content for analysis:\n```\n{st.session_state.uploaded_file_content}\n```\n"})
        st.info(f"Analyzing '{st.session_state.uploaded_file_name}' along with your query...")
    else:
        # Only show this warning if the user input implies they might be asking about a file, but none is there.
        if "file" in user_input.lower() or "code" in user_input.lower() or "troubleshoot" in user_input.lower():
            st.warning("No file content to analyze for this query as no file was successfully uploaded or it was cleared.")


    # Get AI response
    with st.chat_message("Ultronic AI"):
        with st.spinner("Calculating my next simple remark..."):
            full_response = chat_with_gpt(current_messages)
            st.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- New Section for External Link ---
st.markdown("---") # Another separator for clarity
st.subheader("Have Feedback or Want to Connect?")
st.write("If you're interested in sharing more ideas or connecting, please feel free fill out this google survey below:")

# Replace with your desired URL and display text
creator_url = "https://docs.google.com/forms/d/e/1FAIpQLSfSUsHpdBhffbRphQ7ACxfxvQYGkfCWx3apfIcYvXQjj5WuLA/viewform?usp=header" # Example URL
link_text = "Visit Ultronic AI Chatbot Feedback Page"

st.markdown(f"**[{link_text}]({creator_url})**", unsafe_allow_html=False) # target="_blank" is default for external links in Streamlit markdown
st.write("Thank you for using Ultronic AI!")