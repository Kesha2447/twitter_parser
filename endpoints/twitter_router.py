# -*- coding: utf-8 -*-
'''Creating endpoints for getting basic twitter data'''

from random import randrange
from typing import List, Union
from fastapi import APIRouter, BackgroundTasks, Request, Body, Query, Path
from models.models import *
from twitter import logic


router = APIRouter(prefix="/api", tags=['Basic information'])
twitter = logic.Twitter()


@router.post("/usersInfo", response_model=NewSessionResponse)
async def users_info(
    request: Request,
    background_tasks: BackgroundTasks,
    users: List[str] = Body(max_length=500)):
    '''Creates a request to receive Twitter account data, accepts up to 500 links to user pages'''

    client_ip = request.client.host

    try:
        session = int(client_ip.replace('.', '256'))
    except ValueError:
        session = randrange(10000000, 90000000)

    response = twitter.add_session(session, users)
    background_tasks.add_task(twitter.start_parsing)

    return response


@router.get("/users/status", response_model=StatusResponse)
async def status(session_id: int = Query()):
    '''Returns a list of users and the parsing status for each'''

    return twitter.get_status(session_id)


@router.get("/user/{username}", response_model=UserInfoResponse)
async def user(
    session_id: int = Query(),
    username: str = Path(min_length=3, max_length=50)):
    '''Returns some basic user data'''

    return twitter.get_user_info(session_id, username)


@router.get("/tweets/{twitter_id}", tags=['Tweets'], response_model=TweetsResponse)
async def tweets(twitter_id: int = Path()):
    '''Returns the user's last 10 tweets by their twitter_id'''

    return twitter.get_tweets(twitter_id)
