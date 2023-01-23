# -*- coding: utf-8 -*-
'''This module is used to get information about twitter users'''

import time
import urllib
import requests
import traceback
from fastapi import HTTPException
from core.config import PROXY, WAITING_LIMIT, BEARED


class Parser:
    '''A class for parsing twitter data'''

    headers = {
        'content-type': 'application/json',
        'x-twitter-active-user': 'no',
        'x-twitter-client-language': 'en',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-csrf-token': '00000000000000000000000000000000',
        'cookie': 'ct0=00000000000000000000000000000000;',
        'authorization': BEARED,
    }

    def __init__(self, loger):
        if PROXY:
            self.proxies = {
                "http": "http://" + PROXY,
                "https": "https://" + PROXY,
            }
        else:
            self.proxies = None

        self.loger = loger
        self.headers['x-guest-token'] = self._get_guest_token()
        self.headers['cookie'] += 'gt=' + self.headers['x-guest-token']


    def get_folowing(self, login):
        '''Parses user data by his username'''

        url = 'https://api.twitter.com/graphql/hVhfo_TquFTmgL7gYwf91Q/UserByScreenName'

        payload = {
            'variables': '{'+ f'''
                "screen_name": "{login}",
                "withSafetyModeUserFields": true,
                "withSuperFollowsUserFields": true
            ''' + '}',
            'features': '''{
                "responsive_web_twitter_blue_verified_badge_is_enabled": true,
                "verified_phone_label_enabled": false,
                "responsive_web_graphql_timeline_navigation_enabled": true
            }'''
        }

        server_data = self._request(url, payload)
        if server_data.get('status') == 1:
            return server_data

        try:
            user_data = server_data['data']['user']['result']
            user_info = {
                'status': 0,
                'data': {
                    'twitter_id': user_data['rest_id'],
                    'name': user_data['legacy']['name'],
                    'username': user_data['legacy']['screen_name'],
                    'following_count': user_data['legacy']['friends_count'],
                    'followers_count': user_data['legacy']['followers_count'],
                    'description': user_data['legacy']['description'],
                }
            }
            return user_info

        except KeyError:
            if server_data.get('errors'):
                server_data['status'] = 1
                return server_data
            else:
                self.loger.error('twitter_parser.Parser -> get_folowing: Incorrect JSON response: ' + str(server_data))
                return {'status': 1, 'errors': [{'code': 3, 'message': 'Incorrect twiiter response'}]}


    def get_twits(self, twitter_id, limit=10):
        '''Parses user twits by his twitter_id'''

        url = 'https://twitter.com/i/api/graphql/whN_WW_HT--6SW2bhDcx4Q/UserTweets'

        payload = {
            'variables': '{'+ f'''
                "userId": "{twitter_id}",
                "count": {limit+2},
                "includePromotedContent": true,
                "withQuickPromoteEligibilityTweetFields": true,
                "withSuperFollowsUserFields": true,
                "withDownvotePerspective": false,
                "withReactionsMetadata": false,
                "withReactionsPerspective": false,
                "withSuperFollowsTweetFields": true,
                "withVoice": true,
                "withV2Timeline": true
            ''' + '}',
            'features': '''{
                "responsive_web_twitter_blue_verified_badge_is_enabled": true,
                "verified_phone_label_enabled": false,
                "responsive_web_graphql_timeline_navigation_enabled": true,
                "view_counts_public_visibility_enabled": true,
                "view_counts_everywhere_api_enabled": true,
                "tweetypie_unmention_optimization_enabled": true,
                "responsive_web_uc_gql_enabled": true,
                "vibe_api_enabled": true,
                "responsive_web_edit_tweet_api_enabled": true,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": true,
                "standardized_nudges_misinfo": true,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": false,
                "interactive_text_enabled": true,
                "responsive_web_text_conversations_enabled": false,
                "responsive_web_enhance_cards_enabled": false
            }'''
        }

        server_data = self._request(url, payload)
        if server_data.get('status', -1) == 1:
            return server_data

        try:
            user_tweets = server_data['data']['user']['result']['timeline_v2']['timeline']['instructions'][1]['entries']

            user_info = {
                'status': 0,
                'data': []
            }

            for tweet in user_tweets:
                if tweet['entryId'].startswith('tweet'):
                    tweet_text = tweet['content']['itemContent']['tweet_results']['result']['legacy'] #['full_text']
                    user_info['data'].append(tweet_text)

            return user_info

        except KeyError:
            if server_data.get('errors'):
                server_data['status'] = 1
                raise HTTPException(500, detail=server_data)
            else:
                self.loger.error('twitter_parser.Parser -> get_twits: Incorrect JSON response: ' + server_data)
                raise HTTPException(500, detail={'status': 1, 'errors': [{'code': 3, 'message': 'Incorrect twiiter response'}]})


    def _request(self, url, payload):
        '''Makes a request to the server with the specified data and returns an error dictionary or result object'''

        if payload:
            payload_str = urllib.parse.urlencode(payload).replace('%27', '%22').replace('+', '')
            url += '?' + payload_str

        complete = False
        start_time = time.time()
        while not complete:
            try:
                with requests.get(url=url, headers=self.headers, proxies=self.proxies) as response:
                    complete = True

            except requests.exceptions.ConnectionError:
                now = time.time()
                if now - start_time < WAITING_LIMIT:
                    print(f"[{time.ctime(now)}]: A single error in receiving a response.")
                    self.loger.warning('twitter_parser.Parser -> _request: single requests.exceptions.ConnectionError')

                else:
                    print(f"[{time.ctime(now)}]: The request cannot be completed within {WAITING_LIMIT} seconds")
                    self.loger.error('twitter_parser.Parser -> _request: requests.exceptions.ConnectionError' + traceback.format_exc())

                return {'status': 1, 'errors': [{'code': 2, 'message': 'Connection with twiiter servers error'}]}

        try:
            answer = response.json()
            return answer
        except:
            print(f'Not a JSON format: {response.text}')
            self.loger.error('twitter_parser.Parser -> _request: Not a JSON response: ' + response.text)
            return {'status': 1, 'errors': [{'code': 3, 'message': 'Incorrect twitter response'}]}


    def _get_guest_token(self):
        '''Get a guest token for parsing'''

        url = 'https://api.twitter.com/1.1/guest/activate.json'

        complete = False
        start_time = time.time()
        while not complete:
            try:
                with requests.post(url=url, headers=self.headers, proxies=self.proxies) as response:
                    complete = True

            except requests.exceptions.ConnectionError:
                now = time.time()
                if now - start_time > WAITING_LIMIT*2:
                    print(f"[{time.ctime(now)}]: Failed to get a token")
                    self.loger.error('twitter_parser.Parser -> _request: Failed to get a token ' + traceback.format_exc())

        return response.json()['guest_token']