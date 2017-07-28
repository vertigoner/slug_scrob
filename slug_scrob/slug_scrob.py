import sys
import os

sys.path.append(os.path.abspath('./../config'))

from env import *
import requests
import json
import hashlib
import webbrowser
import time

def authenticate(apiKey, secret):
    # fetch request token
    apiSig = hashlib.md5(('api_key' + apiKey + 'methodauth.getToken' + secret).encode('utf-8')).hexdigest()
    token = requests.get('http://ws.audioscrobbler.com/2.0/?'
                         'method=auth.getToken&'
                         'api_key=' + apiKey + '&'
                         'api_sig=' + apiSig + '&'
                         'format=json').json()['token']
    print('token: ' + token)

    # user authentication
    webbrowser.open(('http://www.last.fm/api/auth/?'
                     'api_key=' + apiKey + '&'
                     'token=' + token), 1)

    # fetch web service session
    apiSig = hashlib.md5(('api_key' + apiKey + 'mhodauth.getSessiontoken' + token + secret).encode('utf-8')).hexdigest()

    while True:
        response = requests.get('http://ws.audioscrobbler.com/2.0/?'
                                'method=auth.getSession&'
                                'token=' + token + '&'
                                'api_key=' + apiKey + '&'
                                'api_sig=' + apiSig + '&'
                                'format=json').json()

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
    print('sessionKey: ' + sessionKey)

    return token, sessionKey


def getArtistInfo(apiKey, query):
    response = requests.get('http://ws.audioscrobbler.com/2.0/?'
                            'method=artist.getinfo&'
                            'artist=' + query + '&'
                            'api_key=' + apiKey + '&'
                            'format=json')

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



if __name__ == '__main__':
    apiKey = os.environ.get('LastApiKey')
    secret = os.environ.get('LastSecret')

    token, sessionKey = authenticate(apiKey, secret)

    artistInfo = getArtistInfo(apiKey, sys.argv[1])
    print()
    print('Name: ' + artistInfo['name'])
    print('Listeners: ' + artistInfo['listeners'])
    print('Play Count: ' + artistInfo['playcount'])
    print('Bio: ' + artistInfo['bio'])