import os
import logging

import uvicorn

from chatbot.db.chroma import upload_files


def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)-16s %(levelname)-8s %(message)s ",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    assert os.environ["OPENAI_API_KEY"] is not None

    upload_files()
    uvicorn.run("chatbot.api.skill:app", host="0.0.0.0", port=8000, reload=True)
