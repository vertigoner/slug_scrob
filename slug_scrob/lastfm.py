import sys
import os
import requests
import json
import hashlib
import webbrowser
import time
import six

def authenticate(apiKey, secret):
    # fetch request token
    payload = {'method':'auth.getToken',
               'api_key':apiKey}
    payload['api_sig'] = genApiSig(payload, secret)
    payload['format'] = 'json'

    token = requests.get('http://ws.audioscrobbler.com/2.0/?', payload).json()['token']

    # user authentication
    webbrowser.open(('http://www.last.fm/api/auth/?'
                     'api_key=' + apiKey + '&'
                     'token=' + token), 1)

    # fetch web service session
    payload['method'] = 'auth.getSession'
    payload['token'] = token
    del payload['api_sig']
    del payload['format']
    payload['api_sig'] = genApiSig(payload, secret)
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


def scrobble(apiKey, secret, sessionKey, artist, track):
    timestamp = str(int(time.time()))
    payload = {'method':'track.scrobble',
               'artist':artist,
               'track':track,
               'timestamp':timestamp,
               'api_key':apiKey,
               'sk':sessionKey}

    payload['api_sig'] = genApiSig(payload, secret)
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
    


def getArtistInfo(apiKey, artist, secret):
    payload = {'method':'artist.getInfo',
               'artist':artist,
               'api_key':apiKey}

    payload['api_sig'] = genApiSig(payload, secret)
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


def genApiSig(dataToHash, secret):
    sigStr = ''
    for key in sorted(dataToHash):
        sigStr += key + dataToHash[key]

    sigStr += secret
    return md5(sigStr)


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