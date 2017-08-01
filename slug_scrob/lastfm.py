import sys
import os
import requests
import json
import hashlib
import webbrowser
import time
import six
import pickle

class lastfm():


    def __init__(self):

        self.apiKey = os.environ.get('LastApiKey')
        self.secret = os.environ.get('LastSecret')

        try:
            pCont = pickle.load(open('save.p', 'rb'))
            self.username = pCont['LastUser']
            self.sessionKey = pCont['LastSessionKey']
        except FileNotFoundError:
            self.username, self.sessionKey = self.authenticate()
            pCont = {'LastUser':self.username, 'LastSessionKey':self.sessionKey}
            pickle.dump(pCont, open('save.p', 'wb'))

        if self.apiKey == None or self.secret == None:
            print('Please set your API Key and secret (obtained from last.fm) in config/env.py')
            sys.exit()


    def authenticate(self):

        # fetch request token
        payload = {'method':'auth.getToken',
                   'api_key':self.apiKey}
        payload['api_sig'] = self.genApiSig(payload)
        payload['format'] = 'json'

        token = requests.get('http://ws.audioscrobbler.com/2.0/?', payload).json()['token']

        # user authentication
        webbrowser.open(('http://www.last.fm/api/auth/?'
                         'api_key=' + self.apiKey + '&'
                         'token=' + token), 1)

        # fetch web service session
        payload['method'] = 'auth.getSession'
        payload['token'] = token
        del payload['api_sig']
        del payload['format']
        payload['api_sig'] = self.genApiSig(payload)
        payload['format'] = 'json'

        while True:
            response = requests.get('http://ws.audioscrobbler.com/2.0/?', payload).json()

            if 'session' in response:
                break
            elif 'error' in response:
                if response['error'] != 14:
                    print('Error fetching session:')
                    print('     Error ' + str(response['error']) + ': ' + response['message'])
                    return

            time.sleep(5)

        username = response['session']['name']
        sessionKey = response['session']['key']

        print('username: ' + username)
        print('sk: ' + sessionKey)

        return username, sessionKey


    def scrobble(self, artist, track):

        timestamp = str(int(time.time()))
        payload = {'method':'track.scrobble',
                   'artist':artist,
                   'track':track,
                   'timestamp':timestamp,
                   'api_key':self.apiKey,
                   'sk':self.sessionKey}

        payload['api_sig'] = self.genApiSig(payload)
        payload['format'] = 'json'


        response = requests.post('http://ws.audioscrobbler.com/2.0/', payload)

        if response.status_code == 200:
            if 'error' in response:
                print('Error fetching session:')
                print('     Error ' + str(response['error']) + ': ' + response['message'])

            response = response.json()
            print(str(response))

        else:
            print("Response status code: " + str(response.status_code))
        


    def getArtistInfo(self, artist):

        payload = {'method':'artist.getInfo',
                   'artist':artist,
                   'api_key':self.apiKey}

        payload['api_sig'] = self.genApiSig(payload)
        payload['format'] = 'json'

        response = requests.get('http://ws.audioscrobbler.com/2.0/?', payload)

        if response.status_code == 200:
            response = response.json()

            info = {}
            info['status'] = 'success'
            info['name'] = response['artist']['name']
            info['listeners'] = response['artist']['stats']['listeners']
            info['playcount'] = response['artist']['stats']['playcount']
            info['bio'] = response['artist']['bio']['summary']
            
            return info

        else:
            return {'status':'failure'}


    def genApiSig(self, dataToHash):

        sigStr = ''
        for key in sorted(dataToHash):
            sigStr += key + dataToHash[key]

        sigStr += self.secret
        return md5(sigStr)


# HELPER FUNCTIONS

def md5(text):
    h = hashlib.md5(formatUnicode(text).encode("utf-8"))
    return h.hexdigest()


def formatUnicode(text):

    if isinstance(text, six.binary_type):
        return six.text_type(text, "utf-8")
    elif isinstance(text, six.text_type):
        return text
    else:
        return six.text_type(text)