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

            User: {user_message}
            Intent: 
        """
    ),
    verbose=True,
)
answer_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template = """
            Your job is to answer the query based on information.

            <Information>
            {information}
            <Iinformation>

            <Query>
            {query}
            </Query>
        """
    ),
    verbose=True
)
default_chain = ConversationChain(llm=llm)


def callback_handler(request: ChatbotRequest) -> dict:
    query = request.userRequest.utterance

    intent = parse_intent_chain.run(query)
    if intent in ["kakao_sync", "kakao_channel", "kakao_social"]:
        info = query_db(query)
        context = {"information": info, "query": query}
        output = answer_chain.run(context)
    else:
        output = default_chain.run(query)

    response_callback(output, request)


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
