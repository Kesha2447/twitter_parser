# -*- coding: utf-8 -*-
'''This module is designed to work with the parser'''

import os
import logging
from collections import deque
from threading import Thread
from typing import List
from fastapi import HTTPException
from .our_parser import Parser



def new_loger(name:str, path:str):
    '''Create a new logger using the logging library and perform the initial configuration and connection'''

    dir_name = os.path.dirname(path)
    if dir_name and not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    #Trim the log file if it is too large
    if os.path.exists(path):
        with open(path, 'r') as file:
            content = file.read()

        if len(content) > 2000:
            with open(path, 'w') as file:
                file.write(content[1000:])

    loger = logging.getLogger(name)
    loger.setLevel(logging.INFO)

    fh = logging.FileHandler(path, encoding='utf-8')
    formatter = logging.Formatter("\n-->> %(name)s %(asctime)s %(levelname)s %(message)s", datefmt="%d.%m %H:%M:%S")
    fh.setFormatter(formatter)
    loger.addHandler(fh)

    return loger


class Twitter:
    '''
    A class designed to work with the twitter parser in turn
    ----------------------
    Structure of the session dictionary:

    self.sessions = {
        'session_id': {
            'status': 'pending',
            'users': {
                'username': {
                    'response': None,
                    'info': {
                        'username': username,
                        'status': status,
                        }
                    }
                ...
                }
            }
        ...
    }
    '''

    def __init__(self):
        self.loger = new_loger('Twitter Parser', 'logs/prod.log')
        self.parser = Parser(self.loger)

        self.sessions = {}
        self.is_works = False
        self.conveyor = deque() #Parsing queue (session, username)


    def add_session(self, session: str, users: List[str]) -> dict:
        '''Extracts twitter account logins from links and saves the session'''

        if not users:
            raise HTTPException(400, detail={'status': 1, 'errors': [{'code': 4, 'message': 'The list of users is empty'}]})

        server_session = self.sessions.get(session)
        if not server_session is None and server_session['status'] == 'pending':
            raise HTTPException(400, detail={'status': 1, 'errors': [{'code': 5, 'message': 'The server has an active request from this ip address'}]})

        conveyor_len = len(self.conveyor)
        self.sessions[session] = {'status': 'pending', 'users': {}}

        for link in users:
            _, username = link.rsplit('/', 1)
            self.sessions[session]['users'][username] ={
                'response': None,
                'info': {
                    'username': username,
                    'status': 'pending',
                    }
                }

            self.conveyor.append((session, username))

        self.conveyor.append((session, '||stop||'))

        return {'status': 0, 'data': {'session_id': session, 'queue': conveyor_len}}


    def get_status(self, session: str) -> dict:
        '''Returns a list of users and their parsing status'''

        server_session = self.sessions.get(session)
        if server_session is None:
            raise HTTPException(400, detail={'status': 1, 'errors': [{'code': 6, 'message': 'The session expired or was not created'}]})

        statuses = map(lambda username: server_session['users'][username]['info'], server_session['users'])

        return {'status': 0, 'data': list(statuses)}


    def get_user_info(self, session: str, username: str) -> dict:
        '''Returns information about a specific user'''

        server_session = self.sessions.get(session)
        if server_session is None:
            raise HTTPException(400, detail={'status': 1, 'errors': [{'code': 6, 'message': 'The session expired or was not created'}]})

        server_user = server_session['users'].get(username)
        if server_user is None:
            raise HTTPException(400, detail={'status': 1, 'errors': [{'code': 7, 'message': 'This user was not in the request'}]})

        if server_user['info']['status'] == 'pending':
            raise HTTPException(400, detail={'status': 1, 'errors': [{'code': 8, 'message': 'This user has not been verified yet'}]})

        if server_user['response']['status'] != 0:
            raise HTTPException(500, detail={'status': 1, 'errors': [{'code': 3, 'message': 'Incorrect twiiter response'}]})

        return server_user['response']


    def get_tweets(self, twitter_id: int) -> dict:
        '''Returns a list of the user's last 10 tweets'''

        return self.parser.get_twits(twitter_id)


    def start_parsing(self):
        '''Checks if there are users in the queue, if there are, parses'''

        def parsing(self):
            '''This function will be called in a separate process, as parsing may take time'''

            while len(self.conveyor) > 0:
                session, username = self.conveyor.popleft()

                if username == '||stop||':
                    self.sessions[session]['status'] = 'complete'
                    continue

                response = self.parser.get_folowing(username)

                status = ''
                if response['status'] == 0:
                    status = 'success'
                else:
                    status = 'failed'

                self.sessions[session]['users'][username]['response'] = response
                self.sessions[session]['users'][username]['info']['status'] = status

            self.is_works = False


        if self.is_works:
            return

        if len(self.conveyor) == 0:
            return

        self.is_works = True

        thread = Thread(target=parsing, args=(self,))
        thread.start()
