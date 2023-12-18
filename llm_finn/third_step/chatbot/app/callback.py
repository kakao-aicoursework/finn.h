from os.path import dirname

import requests
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts.chat import ChatPromptTemplate

from chatbot.domain.model import ChatbotRequest
from chatbot.db.chroma import query_db
from chatbot.history import load_conversation_history, get_chat_history, log_user_message, log_bot_message


llm = ChatOpenAI(temperature=0, max_tokens=250, model="gpt-3.5-turbo")

def read_template(path):
    with open(path, "r") as fin:
        return fin.read()

parse_intent_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template = read_template(f"{dirname(__file__)}/template/INTENT_TEMPLATE.txt")
    ),
    verbose=True,
)
answer_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template = read_template(f"{dirname(__file__)}/template/ANSWER_TEMPLATE.txt")
    ),
    verbose=True
)
default_chain = LLMChain(
    llm=llm,
    prompt=ChatPromptTemplate.from_template(
        template = read_template(f"{dirname(__file__)}/template/DEFAULT_TEMPLATE.txt")
    ),
    verbose=True,
)


def callback_handler(request: ChatbotRequest) -> dict:
    conversation_id = request.userRequest.user.id
    
    query = request.userRequest.utterance
    context = {"query": query, "chat_history": get_chat_history(conversation_id)}

    intent = parse_intent_chain.run(context)
    if intent in ["kakao_sync", "kakao_channel", "kakao_social"]:
        info = query_db(query, intent)  # search db with intent
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
