#-*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi import BackgroundTasks
from fastapi.responses import HTMLResponse
import openai

from chatbot.app.callback import callback_handler
from chatbot.domain.model import ChatbotRequest

app = FastAPI()


@app.post("/callback")
async def skill(req: ChatbotRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(callback_handler, req)
    out = {
        "version" : "2.0",
        "useCallback" : True,
        "data": {
            "text" : "생각하고 있는 중이에요😘 \n15초 정도 소요될 거 같아요 기다려 주실래요?!"
        }
    }
    return out
