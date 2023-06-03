'''
카카오 토큰 생성
'''

from info import *
import requests
import json

# KAKAO_API_KEY, KAKAO_AUTH_CODE: https://developers.kakao.com/docs/latest/ko/message/rest-api
URL_GET = 'https://kauth.kakao.com/oauth/token'
REST_API_KEY = KAKAO_API_KEY
REDIRECT_URI = 'https://example.com/oauth'
AUTHORIZE_CODE = KAKAO_AUTH_CODE

data_get = {
    'grant_type':'authorization_code',
    'client_id':REST_API_KEY,
    'redirect_uri':REDIRECT_URI,
    'code': AUTHORIZE_CODE,
    }

response = requests.post(URL_GET, data=data_get)
tokens = response.json()
print(tokens)

# code with token saved to this dir
# DIRECTORY:  for your .json file
with open(DIRECTORY,"w") as fp:
    json.dump(tokens, fp)