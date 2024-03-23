import requests


print(requests.post('http://127.0.0.1:8080/create_user/test').text)