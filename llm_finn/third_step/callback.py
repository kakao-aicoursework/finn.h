import aiohttp
import os
import time
import logging

import openai
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chains import LLMMathChain

from dto import ChatbotRequest
from db import get_kakao_sync_data, get_kakao_channel_data, get_kakao_social_data

openai.api_key = os.environ["API_KEY"]
SYSTEM_MSG = """
You are a Kakao service provider. Please kindly answer user questions.
The conditions below must be met.
- Please answer in Korean.
- Please answer structurally.
- Please summarize your answer in about 200 characters.
"""
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
llm_match_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
tools = [
    Tool(
        name="get_kakao_sync_data",
        func=get_kakao_sync_data,
        description="Used for searches related to Kakao Sync(카카오 싱크).",
    ),
    Tool(
        name="get_kakao_channel_data",
        func=get_kakao_channel_data,
        description="Used for searches related to Kakao Channel(카카오 채널).",
    ),
    Tool(
        name="get_kakao_social_data",
        func=get_kakao_social_data,
        description="Used for searches related to Kakao Social(카카오 소셜).",
    ),
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # zero shot으로 하면 영어로 답하고 무한 루프 돎
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=4,  # 무한 루프 방지
)


async def callback_handler(request: ChatbotRequest) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": request.userRequest.utterance},
    ]

    output_text = agent.run(messages)
    await response_callback(output_text, request)


async def response_callback(output_text, request):
	payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": output_text
                    }
                }
            ]
        }
    }
	url = request.userRequest.callbackUrl

	if url:
		async with aiohttp.ClientSession() as session:
			async with session.post(url=url, json=payload, ssl=False) as resp:
				await resp.json()

