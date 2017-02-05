# coding=utf-8
import os
import json
import time
import getpass
import requests
from requests.auth import AuthBase
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import (
    API_VERSION, APP_VERSION, APP_BUILD, UUID, UA, APP_ZA, CLIENT_ID,
    TOKEN_FILE, LOGIN_URL, CAPTCHA_URL)
from utils import gen_login_signature
from exception import LoginException

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

LOGIN_DATA = {
    'grant_type': 'password',
    'source': 'com.zhihu.ios',
    'client_id': CLIENT_ID
}


class ZhihuOAuth(AuthBase):
    def __init__(self, token=None):
        self._token = token

    def __call__(self, r):
        r.headers['X-API-Version'] = API_VERSION
        r.headers['X-APP_VERSION'] = APP_VERSION
        r.headers['X-APP-Build'] = APP_BUILD
        r.headers['x-app-za'] = APP_ZA
        r.headers['X-UDID'] = UUID
        r.headers['User-Agent'] = UA
        if self._token is None:
            auth_str = 'oauth {client_id}'.format(
               client_id=CLIENT_ID
            )
        else:
            auth_str = '{type} {token}'.format(
                type=str(self._token.token_type.capitalize()),
                token=str(self._token.access_token)
            )
        r.headers['Authorization'] = auth_str
        return r


class ZhihuToken:
    def __init__(self, user_id, uid, access_token, expires_in, token_type,
                 refresh_token, cookie, lock_in=None, unlock_ticket=None):
        self.create_at = time.time()
        self.user_id = uid
        self.uid = user_id
        self.access_token = access_token
        self.expires_in = expires_in
        self.expires_at = self.create_at + self.expires_in
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.cookie = cookie

        # Not used
        self._lock_in = lock_in
        self._unlock_ticket = unlock_ticket

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return cls.from_dict(json.load(f))

    @staticmethod
    def save_file(filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f)

    @classmethod
    def from_dict(cls, json_dict):
        try:
            return cls(**json_dict)
        except TypeError:
            raise ValueError(
                '"{json_dict}" is NOT a valid zhihu token json.'.format(
                    json_dict=json_dict
                ))

class ZhihuClient:
    def __init__(self, token_file=TOKEN_FILE):
        self._session = requests.session()
        self._session.verify = False

        if os.path.exists(token_file):
            self._token = ZhihuToken.from_file(token_file)
        else:
            print('----- Zhihu OAuth Login -----')
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            self._login_auth = ZhihuOAuth()
            json_dict = self.login(username, password)
            ZhihuToken.save_file(token_file, json_dict)
        self.auth = ZhihuOAuth(self._token)

    def login(self, username, password):
        data = LOGIN_DATA.copy()
        data['username'] = username
        data['password'] = password
        gen_login_signature(data)

        if self.need_captcha():
            captcha_image = self.get_captcha()
            with open(CAPTCHA_FILE, 'wb') as f:
                f.write(captcha_image)
            print('Please open {0} for captcha'.format(
                os.path.abspath(CAPTCHA_FILE)))

            captcha = input('captcha: ')
            os.remove(os.path.abspath(CAPTCHA_FILE))
            res = self._session.post(
                CAPTCHA_URL,
                auth=self._login_auth,
                data={'input_text': captcha}
            )
            try:
                json_dict = res.json()
                if 'error' in json_dict:
                    raise LoginException(json_dict['error']['message'])
            except (ValueError, KeyError) as e:
                raise LoginException('Maybe input wrong captcha value')

        res = self._session.post(LOGIN_URL, auth=self._login_auth, data=data)
        try:
            json_dict = res.json()
            if 'error' in json_dict:
                raise LoginException(json_dict['error']['message'])
            self._token = ZhihuToken.from_dict(json_dict)
            return json_dict
        except (ValueError, KeyError) as e:
            raise LoginException(str(e))

    def need_captcha(self):
        res = self._session.get(CAPTCHA_URL, auth=self._login_auth)
        try:
            j = res.json()
            return j['show_captcha']
        except KeyError:
            raise LoginException('Show captcha fail!')


if __name__ == '__main__':
    client = ZhihuClient()
