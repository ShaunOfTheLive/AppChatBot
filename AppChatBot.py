import json
import requests
from urllib.parse import urlencode

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
