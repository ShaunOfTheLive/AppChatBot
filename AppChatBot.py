import json
from urllib.parse import urlencode

import requests
import tinys3

from ConfigDict import ConfigDict

class AppChatBot(object):
    def __init__(self, config_file):
        self.config = ConfigDict(config_file)
        self.base_url = 'https://appchatserver.herokuapp.com'

    def is_registered(self):
        return self.config['accessToken'] is not None

    # API functions
    def register(self):
        urlpath = '/application/newAnonUser'

        r = requests.post(self.base_url + urlpath)

        r_json = r.json() 
        self.config['id'] = r_json['id']
        self.config['username'] = r_json['username']
        self.config['accessToken'] = r_json['accessToken']
        self.config.save()

    def change_username(self, new_username):
        query = urlencode({'oldUsername': self.config['username'],
                           'newUsername': new_username,
                           'accessToken': self.config['accessToken']})
        urlpath = '/application/chooseUsername?%s' % query

        r = requests.post(self.base_url + urlpath)

        # TODO: if request returns "Username already exists.", throw
        # TODO: if returned username does not match new_username, throw?
        # TODO: if hasAccess is false, throw?
        r_json = r.json() 
        self.config['username'] = r_json['username']
        self.config.save()

    def sign_in(self):
        query = urlencode({'username': self.config['username'],
                           'accessToken': self.config['accessToken']})
        urlpath = '/application/userRegistered?%s' % query

        r = requests.post(self.base_url + urlpath)

        # TODO: check if response is 200, otherwise throw

    def get_rooms(self):
        query = urlencode({'username': self.config['username'],
                           'accessToken': self.config['accessToken']})
        urlpath = '/getRooms?%s' % query

        r = requests.get(self.base_url + urlpath)

        r_json = r.json()

        return r_json

    def join_rooms(self, room_list):
        query = urlencode({'username': self.config['username'],
                           'accessToken': self.config['accessToken']})
        urlpath = '/joinRooms?%s' % query
        post_data = json.dumps(room_list)

        r = requests.post(self.base_url + urlpath, data=post_data)

    def mark_messages_seen(self, package_name):
        query = urlencode({'username': self.config['username'],
                           'accessToken': self.config['accessToken'],
                           'packageName': package_name})
        urlpath = '/markMessagesSeen?%s' % query

        r = requests.post(self.base_url + urlpath)

    def get_messages(self, package_name):
        query = urlencode({'packageName': package_name})
        urlpath = '/getMessages?%s' % query

        r = requests.post(self.base_url + urlpath)

        r_json = r.json()

        return r_json

    def post_message(self, package_name, message):
        query = urlencode({'username': self.config['username'],
                           'accessToken': self.config['accessToken'],
                           'packageName': package_name,
                           'messageText': message})
        urlpath = '/application/postMessage?%s' % query

        print(self.base_url + urlpath)
        r = requests.post(self.base_url + urlpath)
        r.raise_for_status()

    # TODO: post image message
    def post_image(self, package_name, filename):
        url = 'https://cognito-identity.us-east-1.amazonaws.com/'
        post_data = '{"IdentityPoolId":"us-east-1:dd019d8a-7b9d-487d-b0c8-61d904fb8c6a","Logins":{}}'
        headers = {'X-Amz-Target': 'AWSCognitoIdentityService.GetId',
                   'Content-Type': 'application/x-amz-json-1.0'}

        r = requests.post(url, headers=headers, data=post_data)

        identity_id = r.text
        print(identity_id)

        post_data = identity_id
        headers['X-Amz-Target'] = 'AWSCognitoIdentityService.GetCredentialsForIdentity'

        r = requests.post(url, headers=headers, data=post_data)

        credentials = r.json()

        S3_ACCESS_KEY = credentials['Credentials']['AccessKeyId']
        S3_SECRET_KEY = credentials['Credentials']['SecretKey']
        print(S3_ACCESS_KEY)
        print(S3_SECRET_KEY)
        import hashlib
        import base64
        m = hashlib.md5()
        hash = hashlib.md5(open(filename, 'rb').read()).hexdigest()
        hash = base64.b64encode(hash.encode('utf-8')).decode('utf-8')
        print(hash)
        print(credentials['Credentials']['SessionToken'])
        headers={'x-amz-security-token': credentials['Credentials']['SessionToken'],
                 'Content-MD5': hash,
                 'Expect': '100-continue'}
        from tinys3.auth import S3Auth
        print(S3Auth(S3_ACCESS_KEY, S3_SECRET_KEY))
        r = requests.get('http://appchat-screenshots.s3.amazonaws.com/?location', auth=S3Auth(S3_ACCESS_KEY, S3_SECRET_KEY), headers=headers)
        print(r.text)
        
        conn = tinys3.Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
#        conn.delete('testname-Screenshot_2015-05-01-21-36-57.png', 'appchat-screenshots')
#        print(str(list(conn.list('screenshot', 'appchat-screenshots'))))

        with open(filename, 'rb') as f:
            conn.upload(filename, f, bucket='appchat-screenshots', headers=headers)

        r.raise_for_status()

        query = urlencode({'username': self.config['username'],
                           'accessToken': self.config['accessToken'],
                           'packageName': package_name,
                           'imageKey': filename})
        urlpath = '/application/postMessage?%s' % query

        r = requests.post(self.base_url + urlpath)

