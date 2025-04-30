from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from datetime import datetime

class MeetingMessage(BaseMessage):
    type: Literal["system"] = "meeting  "

from chat_queue import ChatQueueList
from prompt_manger import PromptManager
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import config

_config: dict = {"configurable": {"session_id": "user"}}


if 'llm' not in st.session_state:
    st.session_state.llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=config.GEMINI_API_KEY)

if 'meeting_form_is_allowed' not in st.session_state:
    st.session_state.meeting_form_is_allowed = False

if 'meeting_form' not in st.session_state:
    st.session_state.meeting_form = {}

if 'prompts' not in st.session_state:
    st.session_state.prompt_manager = PromptManager(st.session_state.llm)

def get_date_for_today() -> str:

    today = datetime.today()
    days_of_tr: dict[str, str] = {
        "Monday": "Pazartesi",
        "Tuesday": "Salı",
        "Wednesday": "Çarşamba",
        "Thursday": "Perşembe",
        "Friday": "Cuma",
        "Saturday": "Cumartesi",
        "Sunday": "Pazar"
    }
    day_name = today.strftime('%A')
    tr_day_name = days_of_tr[day_name]
    today = today.strftime('%d %m %Y')
    return f'{today} ({day_name} || {tr_day_name})'

if 'chat_queue' not in st.session_state:
    st.session_state.chat_queue = ChatQueueList(
        rock_items=[
            SystemMessage(content=st.session_state.prompt_manager.task.prompt.format(time_detail=get_date_for_today()))
        ]
    )

def show_meeting_form():
    meeting = st.session_state.meeting_form
    with st.form('meeting_form'):
        st.write("Toplantı detayları")
        st.text_input('title', value=meeting.get('title', ''))
        st.text_input('email', value=meeting.get('email', ''))
        st.text_area('notes', value=meeting.get('notes', ''))
        st.date_input('date', value=meeting.get('date', 'today'))
        st.form_submit_button('Gönder')




st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout='wide'
)

user_input = st.chat_input()
if user_input:
    st.session_state.chat_queue.add(HumanMessage(content=user_input))
    clean_history = [
        chat
        for chat in st.session_state.chat_queue
        if isinstance(chat, (SystemMessage, HumanMessage, AIMessage))
    ]
    model_reply = st.session_state.llm.invoke(clean_history, config=_config)
    st.session_state.chat_queue.add(AIMessage(content=model_reply.content))
    chat_history = [
        chat.content
        for chat in st.session_state.chat_queue
        if isinstance(chat, (HumanMessage, AIMessage))
    ]
    try:
        if meeting := st.session_state.prompt_manager.meeting_creator.chain.invoke({
            "chat_messages_text": ' '.join(chat_history),
            "time_detail": get_date_for_today()
        }):
            print('giriş')
            print(meeting.__dict__)
            st.session_state.meeting_form.update(**meeting.__dict__)
    except Exception as e:
        raise e

for message in st.session_state.chat_queue:
    if isinstance(message, MeetingMessage):
        st.markdown(message.content)
    if isinstance(message, (HumanMessage, AIMessage)):
        role = 'AI' if isinstance(message, AIMessage) else 'User'
        with st.chat_message(role):
            st.markdown(message.content)

if not st.session_state.meeting_form_is_allowed and st.session_state.meeting_form:
    show_meeting_form()