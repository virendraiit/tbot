import time
from openai import OpenAI
from openai import AssistantEventHandler
import streamlit as st

st.set_page_config(page_title="TBot", page_icon=":speech_balloon")  

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant_id=st.secrets["ASSISTANT_ID"]
thread = client.beta.threads.create()

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = thread.id



# Create Session state variable to pick openai model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

# Initialize the chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app return
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input(" What is up?")

if prompt:
    
    #Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})


    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        #Openai streaming response
        stream = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            },
            stream=True
        )

        for event in stream:
            if event.data.object == "thread.message.delta":
                #Iterate over content in the delta
                for content in event.data.delta.content:
                    if content.type == 'text':
                        #Print the value field from text deltas
                        full_response += content.text.value
                        message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
                        