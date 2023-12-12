import aiohttp
import os
import time
import logging

import openai
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chains import LLMMathChain

from dto import ChatbotRequest
from db import get_kakao_sink_data

openai.api_key = os.environ["API_KEY"]
SYSTEM_MSG = "당신은 카카오 서비스 제공자입니다. 사용자 질문에 친절하게 답해주세요."
llm = ChatOpenAI(temperature=0)
llm_match_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
tools = [
    Tool(
        name="get_kakao_sink_data",
        func=get_kakao_sink_data,
        description="카카오 싱크에 관한 질문에 답할 때 유용합니다."
    )
]


async def callback_handler(request: ChatbotRequest) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": request.userRequest.utterance},
    ]

    agent = initialize_agent(
        tools, llm, agent="zero-shot-react-description", verbose=True
    )

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

