import sys
import os
import pickle

sys.path.append(os.path.abspath('./../config'))

from env import *
from lastfm import *

if __name__ == '__main__':
    apiKey = os.environ.get('LastApiKey')
    secret = os.environ.get('LastSecret')
    
    try:
        pCont = pickle.load(open('save.p', 'rb'))
        sessionKey = pCont['LastSessionKey']
    except FileNotFoundError:
        username, sessionKey = authenticate(apiKey, secret)
        pCont = {'LastUser':username, 'LastSessionKey':sessionKey}
        pickle.dump(pCont, open('save.p', 'wb'))

    if apiKey == None or secret == None:
        print('Please set your API Key and secret (obtained from last.fm) in config/env.py')
        sys.exit()

    scrobble(apiKey, secret, sessionKey, sys.argv[1], sys.argv[2])

    artistInfo = getArtistInfo(apiKey, sys.argv[1], secret)
    print()
    print('Name: ' + artistInfo['name'])
    print('Listeners: ' + artistInfo['listeners'])
    print('Play Count: ' + artistInfo['playcount'])
    print('Bio: ' + artistInfo['bio'])