import jwt
url ='https://auth.siliconsolutions.co.ke/auth/generate' 
secret = 'J9EjEBmPSoAMbZ7inqmlnCsdm7W0OTN3vLVojI4KZDiWLYhh9iql4T'
username='r.wafula'
password = 'Shika!s@n@!'
import requests
headers= {'username':username, 'secret':secret}
#encoded = jwt.encode({'username': username, 'password':password}, secret, algorithm='HS256')
r = requests.get(url, headers=headers)
print
print 'Requesting token'
print r.url
print r.content
exit()
json = r.json()
auth = json.get('token')
data={'password': 'Shika!s@n@!'}
url2 = 'https://auth.siliconsolutions.co.ke/password/generate'
headers = {'username':username, 'secret':secret, 'Authorization':'Bearer '+auth,'Content-Type':'application/x-www-form-urlencoded'}
r2 = requests.post(url2, data=data, headers=headers)
print 
print 'Setting Pasword'
print 'Payload', data
print r2.content
exit()
url3='https://auth.siliconsolutions.co.ke/secret/generate'
secret ='sikomi((020Licja6827926Maktes0Hyas==Da726952$$@*0hVsagDiamond--29Wasaf1780'
headers = {'username':username, 'password':data.get('password'), 'Authorization':'Bearer '+auth,'Content-Type':'application/x-www-form-urlencoded'}
#print headers
dat={'secret':'7baiuhwdbqwuite6ghadid 0(dayu$#@g e#b8973abjd==@'}
r3 = requests.post(url3, data=dat, headers=headers)
print
print 'Setting new secret'
print 'Headers =>', headers
print r3.content

