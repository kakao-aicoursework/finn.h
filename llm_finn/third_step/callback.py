import os
import time
import logging

import requests
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts.chat import ChatPromptTemplate

from dto import ChatbotRequest
from db import query_db
from history import load_conversation_history, get_chat_history, log_user_message, log_bot_message

assert os.environ["OPENAI_API_KEY"] is not None


llm = ChatOpenAI(temperature=0, max_tokens=250, model="gpt-3.5-turbo")

parse_intent_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template = """
            Your job is to select one intent from the <intent_list>.

            <intent_list>
            1. kakao_sync: question about kakao sync(카카오 싱크).
            2. kakao_channel: question about kakao channel(카카오 채널).
            3. kakao_social: question about kakao social(카카오 소셜).
            </intent_list>

            User: {query}
            Intent: 
        """
    ),
    verbose=True,
)
answer_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template = """
            Your job is to answer the query based on <information> and <chat_history>.

            <Information>
            {information}
            <Iinformation>

            {chat_history}
            <Query>
            {query}
            </Query>
        """
    ),
    verbose=True
)
default_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template= """
            Your job is to read the <query>, Answer the question very detailed.

            {chat_history}
            User: {query}
            Answer:
        """
    ),
    verbose=True,
)


def callback_handler(request: ChatbotRequest) -> dict:
    conversation_id = request.userRequest.user.id
    
    query = request.userRequest.utterance
    context = {"query": query, "chat_history": get_chat_history(conversation_id)}

    intent = parse_intent_chain.run(context)
    if intent in ["kakao_sync", "kakao_channel", "kakao_social"]:
        info = query_db(query)  # search db
        context.update({"information": info})

        output = answer_chain.run(context)
    else:
        output = default_chain.run(context)
    response_callback(output, request)

    # save history
    history_file = load_conversation_history(conversation_id)
    log_user_message(history_file, query)
    log_bot_message(history_file, output)


def response_callback(output_text, request):
	payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                { "simpleText": { "text": output_text } }
            ]
        }
    }
	url = request.userRequest.callbackUrl

	if url:
		requests.post(url=url, json=payload)
