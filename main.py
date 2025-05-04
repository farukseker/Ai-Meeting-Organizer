import time

import requests
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from messages import MeetingMessage
from datetime import datetime
from models import MeetingFormModel
from chat_queue import ChatQueueList
from prompt_manger import PromptManager
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import config
from email_validator import validate_email
from langdetect import detect as langdetect


_config: dict = {"configurable": {"session_id": "user"}}

def load_chat() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model='gemini-2.0-flash', google_api_key=config.GEMINI_API_KEY)

if 'llm' not in st.session_state:
    st.session_state.llm = None

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
    blog_data = 'THERE WAS A PROBLEM WHILE TAKING BLOG DATA FROM THE API'
    if blog_r := requests.get(config.api / 'content/all/?content_type=blog'):
        blog_data = '\n'.join([':'.join([blog.get('title'), blog.get('text')]) for blog in blog_r.json()])

    project_data = 'THERE WAS A PROBLEM WHILE TAKING PROJECT DATA FROM THE API'
    if project_r := requests.get(config.api / 'content/all/?content_type=blog'):
        project_data = '\n'.join([f'^{index + 1}. {project.get('title')}' for index, project in enumerate(project_r.json())])

    st.session_state.chat_queue = ChatQueueList(
        rock_items=[
            SystemMessage(content=st.session_state.prompt_manager.task.prompt.format(
                time_detail=get_date_for_today(),
                faruk_age=str(datetime.now().year - 2000),
                blogs=blog_data,
                projects=project_data,
            ))
        ]
    )


def show_meeting_form():
    meeting = st.session_state.meeting_form
    with (st.form('meeting_form')):
        st.write("Meeting Details")

        title = st.text_input('**Title***', value=meeting.get('title', ''))
        if not title:
            st.error('Title cannot be empty')
        email = st.text_input('**Email***', value=meeting.get('email', ''))
        try:
            validate_email(email)
        except:
            st.error('Email is not valid')

        notes = st.text_area('Notes (optional)', value=meeting.get('notes', ''))

        date_col, time_col = st.columns(2)
        date = date_col.date_input('**Date***', value=meeting.get('date', 'today'))
        time = time_col.time_input('**Time***', value=meeting.get('time', 'now'))
        if not all([date, time]):
            st.error('Date cannot be empty')
        send = st.form_submit_button('Send')
        if send and (meeting_form := MeetingFormModel(title, email, notes, date, time)):
            if (
                response := requests.post(
                    config.api / 'chat/organize-meeting',
                    data=meeting_form.__dict__
                )
            ) and (
                response.status_code == 201
            ):
                st.success(
                    'Meeting create with successful,'
                    f'and sended meeting detail at the your mail {meeting_form.email} too '
                )
                data = response.json()
                st.markdown(f"""
                ### Your meeting has been created. 
                > When your meeting is approved, you will receive a notification to your email address. Have a nice day.
                > {data.get('meeting_id')}
                """)


def get_clean_history_with(*withs):
    return [
        chat.content
        for chat in st.session_state.chat_queue
        if isinstance(chat, withs)
    ]

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout='wide'
)

if st.session_state.meeting_form_is_allowed and st.session_state.meeting_form:
    st.button('A Meeting ')

user_input = st.chat_input()
if user_input:
    if st.session_state.llm is None:
        st.session_state.llm = load_chat()
        time.sleep(.5)
    st.session_state.chat_queue.add(HumanMessage(content=user_input))
    model_reply = st.session_state.llm.invoke(
        get_clean_history_with(SystemMessage, HumanMessage, AIMessage),
        config=_config
    )
    st.session_state.chat_queue.add(AIMessage(content=model_reply.content))
    try:
        history = get_clean_history_with(HumanMessage, AIMessage)
        is_user_lang_tr = langdetect(user_input) == 'tr'
        prompt = st.session_state.prompt_manager.get(
                       'meeting_creator_tr' if is_user_lang_tr else 'meeting_creator'
                    )
        prompt.set_llm(st.session_state.llm)
        meeting = prompt.chain.invoke({
            "chat_messages_text": ' '.join(history),
            "time_detail": get_date_for_today()
        })

        if meeting:
            st.session_state.meeting_form.update(**meeting.__dict__)
    except Exception as e:
        st.error(f'Error {str(e)}')

for message in st.session_state.chat_queue:
    if isinstance(message, MeetingMessage):
        st.markdown(message.content)
    if isinstance(message, (HumanMessage, AIMessage)):
        role = 'AI' if isinstance(message, AIMessage) else 'User'
        with st.chat_message(role):
            st.markdown(message.content)

if not st.session_state.meeting_form_is_allowed and st.session_state.meeting_form:
    show_meeting_form()
