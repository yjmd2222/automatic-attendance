'''
카카오 메시지 발송
'''

import requests
import json
from info import *

link = 'example'

# start kakao
# DIRECTORY:  for your .json file
with open(DIRECTORY,"r") as fp:
    tokens = json.load(fp)

url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

# 사용자 토큰
headers = {
    "Authorization": "Bearer " + tokens['access_token']
}


data = {
    "template_object" : json.dumps({ "object_type" : "text",
                                    "text" : f"{link}",
                                    "link" : {
                                                "web_url" : "www.naver.com"
                                            }
    })
}

response = requests.post(url, headers=headers, data=data)
print(response.status_code)
if response.json().get('result_code') == 0:
    print('메시지를 성공적으로 보냈습니다.')
else:
    print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(response.json()))