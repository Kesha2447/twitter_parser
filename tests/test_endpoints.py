# -*- coding: utf-8 -*-
'''Testing data parsing via rest api'''

import os
import sys
import time
import unittest
from fastapi.testclient import TestClient
os.chdir('..')
sys.path.append(".")
from main import app


client = TestClient(app)


class TestEndpoints(unittest.TestCase):
    '''Testing endpoints'''

    session_id = None


    def test_users_info_success(self):
        response = client.post("/api/usersInfo", json=["https://twitter.com/elonmusk",
                                "https://twitter.com/VitalikButerin", "https://twitter.com/jack",
                                "https://twitter.com/balajis", "https://twitter.com/cdixon",
                                "https://twitter.com/pmarca", "https://twitter.com/brian_armstrong",
                                "https://twitter.com/naval"])


        answer = response.json()
        self.session_id = answer['data']['session_id']

        assert response.status_code == 200
        assert answer['status'] == 0
        assert isinstance(self.session_id, int)


    def test_status_success(self):
        if self.session_id is None:
            self.test_users_info_success()

        response = client.get(f"/api/users/status?session_id={self.session_id}")

        assert response.status_code == 200

        answer = response.json()
        assert answer['status'] == 0
        assert isinstance(answer['data'], list)
        assert len(answer['data']) == 8


    def test_user_success(self):
        if self.session_id is None:
            self.test_users_info_success()

        response = client.get(f"/api/user/elonmusk?session_id={self.session_id}")

        if response.status_code == 400:
            error_code = response.json()['detail']['errors'][0]['code']

            if error_code == 8:
                time.sleep(1)
                return self.test_user_success()

        assert response.status_code == 200

        answer = response.json()
        assert answer['status'] == 0
        assert isinstance(answer['data'], dict)
        assert len(answer['data']) == 6


    def test_tweets_success(self):
        response = client.get("/api/tweets/44196397")

        assert response.status_code == 200

        answer = response.json()
        assert answer['status'] == 0
        assert isinstance(answer['data'], list)
        assert len(answer['data']) <= 12


if __name__ == '__main__':
    unittest.main()