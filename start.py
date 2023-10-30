import streamlit as st
import openai
import mysql.connector

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'admin@1234',
    'database': 'chatbot_db',  # The name of your database
}

# Establish a connection to the MySQL server
connection = mysql.connector.connect(**db_config)

# Create a cursor object to interact with the database
cursor = connection.cursor()

def write_to_db(msg):
    # persona, txt = msg[0], msg[1]
    insert_query = "INSERT INTO chatbot (persona, comments) VALUES (%s, %s)"
    cursor.execute(insert_query, msg)


# Set up the layout
st.set_page_config(page_title="ChatGPT UI", layout="centered")

# Custom CSS to hide the label and create a scrollable container
custom_css = """
<style>
.stTextInput > div:first-child > label {
    display: none;
}
.scrollable-container {
    height: 400px;
    overflow-y: scroll;
}
.small-header {
    font-size: 24px;
    margin-top: -15px;
        margin-bottom: 15px;
}
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Set up OpenAI API
openai.api_key = st.secrets["openai_api_key"]

# Function to get response from OpenAI API
def get_openai_response(user_input, message_history):
    # Convert message history to the format required by the API
    api_messages = [{"role": msg.split(': ')[0].lower(), "content": msg.split(': ')[1]} for msg in message_history]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=api_messages,
        max_tokens=200,
        temperature=0.1,
        n=1,
        stream=False
    )
    return response.choices[0].message['content']

st.image("https://d1hbpr09pwz0sk.cloudfront.net/logo_url/deloitte-uk-850cb991")
col1, col2 = st.columns((2, 1))
col1.title("Deloitte Auditor Enterprise Chat UI")
col1.markdown("<div class='small-header'>We help you with questions related to filing US tax!</div>", unsafe_allow_html=True)

# Store messages
system_message = "System: You're a GPT tax advisor bot (v0.0.1). Your job is to help prepare a tax return by asking questions, then preparing a final tax document. Make sure you only respond with one question at a time."
initial_prompt = "Assistant: Hello! I'm your friendly GPT tax advisor bot. You can ask for help, more details, or a summary at any time. Let's get started! Where are you located?"

# Initialize messages in session_state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [system_message, initial_prompt]

with col1.container() as scrollable_container:
    for message in st.session_state.messages[1:]:
        with st.markdown('<div class="scrollable-container">', unsafe_allow_html=True):
            st.markdown(f'<p>{message}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input field at the bottom of the window
with col1:
    st.write("Your message:")
    # Use a form to handle input field and Send button
    with st.form(key="message_form"):
        user_input = st.text_input("Type your message here...", value="", key="user_input")
        submit_button = st.form_submit_button("Send")


# Get response from OpenAI API and display it
if submit_button:
    user_message = f"User: {user_input}"
    write_to_db(["User", user_message])
    st.session_state.messages.append(user_message)
    response = get_openai_response(user_input, st.session_state.messages)
    write_to_db(["Bot", response])
    bot_message = f"Assistant: {response}"
    st.session_state.messages.append(bot_message)

    st.write('<script>document.querySelector("user_input").value = "";</script>', unsafe_allow_html=True)
    # Clear input after sending the message and rerun the app
    st.rerun()

    col1.markdown('<div style="size:9px">Built by <a href="https://twitter.com/ruv">@rUv</a> | USE AT YOUR OWN RISK</div>', unsafe_allow_html=True)