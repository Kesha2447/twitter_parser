# -*- coding: utf-8 -*-
'''A module for processing requests for information about twitter users using FastAPI'''

import fastapi
import uvicorn
from endpoints import twitter_router


app = fastapi.FastAPI()
app.include_router(twitter_router.router)

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8000)