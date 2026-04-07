import requests
from bs4 import BeautifulSoup
session = requests.Session()
res = session.get('http://127.0.0.1:5003/register')
soup = BeautifulSoup(res.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
print(f"CSRF Token: {csrf_token}")
data = {
    'csrf_token': csrf_token,
    'username': 'post_test',
    'email': 'post@test.com',
    'password': 'password',
    'confirm_password': 'password',
    'submit': 'Sign Up'
}
res2 = session.post('http://127.0.0.1:5003/register', data=data)
print(f"Status Code: {res2.status_code}")
if "Account created" in res2.text or res2.status_code == 302:
    print("Success")
else:
    print("Failure check logs")
