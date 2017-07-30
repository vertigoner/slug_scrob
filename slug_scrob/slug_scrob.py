import sys
import os

sys.path.append(os.path.abspath('./../config'))

from env import *
import requests
import json
import hashlib
import webbrowser
import time
import six

def authenticate(apiKey, secret):
    # fetch request token
    apiSig = hashlib.md5(('api_key' + apiKey + 'methodauth.getToken' + secret).encode('utf-8')).hexdigest()
    payload = {'method':'auth.getToken',
               'api_key':apiKey,
               'api_sig':apiSig,
               'format':'json'}
    token = requests.get('http://ws.audioscrobbler.com/2.0/?', payload).json()['token']
    print('token: ' + token)

    # user authentication
    webbrowser.open(('http://www.last.fm/api/auth/?'
                     'api_key=' + apiKey + '&'
                     'token=' + token), 1)

    # fetch web service session
    apiSig = hashlib.md5(('api_key' + apiKey + 'methodauth.getSessiontoken' + token + secret).encode('utf-8')).hexdigest()
    payload['method'] = 'auth.getSession'
    payload['token'] = token
    payload['api_sig'] = apiSig

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
    print('sessionKey: ' + sessionKey)

    return token, sessionKey


def scrobble(apiKey, secret, sessionKey, artist, track):
    timestamp = str(int(time.time()))
    payload = {'method':'track.scrobble',
               'artist':artist,
               'track':track,
               'timestamp':timestamp,
               'api_key':apiKey,
               'secret':secret,
               'sk':sessionKey}

    sigStr = ''
    for key in sorted(payload):
        sigStr += key + payload[key]

    sigStr += secret
    apiSig = md5(sigStr)

    payload['api_sig'] = apiSig
    payload['format'] = 'json'


    response = requests.post('http://ws.audioscrobbler.com/2.0/', payload)

    print(str(response.json()))


def getArtistInfo(apiKey, artist):
    response = requests.get('http://ws.audioscrobbler.com/2.0/?'
                            'method=artist.getInfo&'
                            'artist=' + artist + '&'
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


def md5(text):
    h = hashlib.md5(format_unicode(text).encode("utf-8"))

    return h.hexdigest()


def format_unicode(text):
    if isinstance(text, six.binary_type):
        return six.text_type(text, "utf-8")
    elif isinstance(text, six.text_type):
        return text
    else:
        return six.text_type(text)


if __name__ == '__main__':
    apiKey = os.environ.get('LastApiKey')
    secret = os.environ.get('LastSecret')

    try:
        token, sessionKey = authenticate(apiKey, secret)
    except TypeError:
        sys.exit()

    scrobble(apiKey, secret, sessionKey, sys.argv[1], sys.argv[2])

    artistInfo = getArtistInfo(apiKey, sys.argv[1])
    print()
    print('Name: ' + artistInfo['name'])
    print('Listeners: ' + artistInfo['listeners'])
    print('Play Count: ' + artistInfo['playcount'])
    print('Bio: ' + artistInfo['bio'])