from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from dashscope import Generation
from http import HTTPStatus
import json

DASHSCOPE_API_KEY="sk-5d42bde55f054728914cb64ac29c89f4"
openai_secret_key=DASHSCOPE_API_KEY

@api_view(['GET','POST'])
def chat_api(request):
    message = request.GET['msg']
    print(message)

    response = Generation.call(
        api_key=DASHSCOPE_API_KEY,
        model='qwen-v1',
        prompt=message
    )
    #requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    response_data = response
    print(response_data)
    text = response_data["output"]["text"]
    return Response({'text': text})