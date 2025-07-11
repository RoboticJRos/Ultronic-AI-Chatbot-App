# Johnny Ros's Ultronic AI App - Further Enhanced Version
# This is a chatbot application using OpenAI's GPT-3.5-turbo model.
import streamlit as st
import openai
import time
from datetime import datetime

# Set page config first
st.set_page_config(
    page_title="Ultronic AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set the OpenAI API key securely using st.secrets
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API key not found. Please set it in .streamlit/secrets.toml")
    st.stop()

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
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt_messages,
            temperature=0.7,
            max_tokens=1000
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
    st.session_state.file_uploader_key += 1
    st.rerun()

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({'role': 'system', 'content': f"{rules}"})
if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Chat statistics
    st.subheader("📊 Chat Statistics")
    st.metric("Messages Sent", st.session_state.chat_counter)
    st.metric("Files Uploaded", 1 if st.session_state.uploaded_file_content else 0)
    
    st.markdown("---")
    
    # Model settings
    st.subheader("🎛️ Model Configuration")
    st.info("Currently using: GPT-3.5-turbo")
    
    st.markdown("---")
    
    # Clear button in sidebar
    if st.button("🗑️ Clear Chat & Files", use_container_width=True):
        clear_chat_history()
        st.success("Chat cleared!")
    
    st.markdown("---")
    
    # Help section
    st.subheader("❓ Help")
    with st.expander("How to use"):
        st.write("""
        1. **Upload a file** (optional) - Python, Arduino, Java, or PLC files
        2. **Ask questions** about your code or general programming
        3. **Get feedback** and troubleshooting help
        4. **Use the clear button** to start fresh
        """)

# --- Main App Layout ---
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🤖 Ultronic AI Chatbot")

with col2:
    st.markdown("### Status")
    if st.session_state.uploaded_file_content:
        st.success("📁 File Loaded")
    else:
        st.info("📁 No File")

st.write("Hello there, fellow BYUI student, faculty, staff or Industrial worker. I'm Ultronic AI, your direct yet honest assistant.")
st.write("How may I help you at this time?")

# --- File Upload Section ---
st.subheader("📤 Upload Program File")

# Create two columns for file upload
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Drag and drop or browse for files:",
        type=[
            "py", "ipynb", # Python
            "ino", "c", "cpp", "h", # Arduino IDE (C/C++ based)
            "java", "jar", "class", # Java
            "rsl", "acd", "rss", "rsp", "l5x", "pro", "prj", "s7p", "cxp", "opt", "onw", "gwb", "gsr", "mwp", "xar", "plc",
            "txt", "log", "md", "json", "xml"
        ],
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )

with col2:
    if st.session_state.uploaded_file_content:
        st.success("✅ File Ready")
        file_size = len(st.session_state.uploaded_file_content.encode('utf-8')) / 1024
        st.metric("File Size", f"{file_size:.1f} KB")

# Process uploaded file
if uploaded_file is not None:
    if st.session_state.uploaded_file_name != uploaded_file.name or (uploaded_file.name and st.session_state.uploaded_file_content is None):
        encodings_to_try = ["utf-8", "latin-1", "cp1252"]
        decoded_successfully = False
        file_content_temp = None

        # Show progress bar while processing
        progress_bar = st.progress(0)
        
        for i, encoding in enumerate(encodings_to_try):
            progress_bar.progress((i + 1) / len(encodings_to_try))
            try:
                uploaded_file.seek(0)
                file_content_temp = uploaded_file.read().decode(encoding)
                decoded_successfully = True
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                st.error(f"Error reading file with '{encoding}': {e}")
                break

        progress_bar.empty()

        if decoded_successfully:
            st.session_state.uploaded_file_content = file_content_temp
            st.session_state.uploaded_file_name = uploaded_file.name
            st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        else:
            st.error("❌ Could not decode file. Please ensure it's a text-based code file.")
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
else:
    if st.session_state.uploaded_file_content is not None:
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_name = None

# Display file content preview
if st.session_state.uploaded_file_content is not None:
    with st.expander(f"👀 Preview: '{st.session_state.uploaded_file_name}'", expanded=False):
        file_extension = st.session_state.uploaded_file_name.split('.')[-1].lower()
        
        # Language mapping for syntax highlighting
        language_map = {
            "py": "python", "ipynb": "python",
            "ino": "c++", "c": "c++", "cpp": "c++", "h": "c++",
            "java": "java", "jar": "java", "class": "java",
        }
        
        language = language_map.get(file_extension, "text")
        
        # Show only first 50 lines for preview
        lines = st.session_state.uploaded_file_content.split('\n')
        preview_content = '\n'.join(lines[:50])
        if len(lines) > 50:
            preview_content += f"\n... ({len(lines) - 50} more lines)"
        
        st.code(preview_content, language=language)

st.markdown("---")

# --- Chat Interface ---
st.subheader("💬 Chat with Ultronic AI")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Ask me about your code or general programming..."):
    # Increment chat counter
    st.session_state.chat_counter += 1
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare messages for AI
    current_messages = list(st.session_state.messages)

    if st.session_state.uploaded_file_content:
        current_messages.append({
            "role": "user", 
            "content": f"The user has uploaded a file named '{st.session_state.uploaded_file_name}' with the following content for analysis:\n```\n{st.session_state.uploaded_file_content}\n```\n"
        })
        st.info(f"🔍 Analyzing '{st.session_state.uploaded_file_name}' along with your query...")

    # Get AI response with typing indicator
    with st.chat_message("assistant"):
        with st.spinner("🤖 Ultronic AI is thinking..."):
            full_response = chat_with_gpt(current_messages)
            
            # Simulate typing effect (optional)
            message_placeholder = st.empty()
            full_response_words = full_response.split()
            displayed_response = ""
            
            for word in full_response_words:
                displayed_response += word + " "
                message_placeholder.markdown(displayed_response + "▌")
                time.sleep(0.05)  # Adjust speed as needed
            
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Footer Section ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Feedback")
    st.write("Share your thoughts and ideas:")
    survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSfSUsHpdBhffbRphQ7ACxfxvQYGkfCWx3apfIcYvXQjj5WuLA/viewform?usp=header"
    st.markdown(f"**[📊 Feedback Survey]({survey_url})**")

with col2:
    st.subheader("👨‍💻 Connect")
    st.write("Get in touch with the creator:")
    creator_url = "https://www.linkedin.com/in/johnny-ros-cit/"
    st.markdown(f"**[💼 Johnny Ros's LinkedIn]({creator_url})**")

st.markdown("---")
st.markdown("*Thank you for using Ultronic AI! 🤖*")
