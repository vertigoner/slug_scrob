import sys
import os
import requests
import json


def getArtistInfo(query):
    response = requests.get('http://ws.audioscrobbler.com/2.0/?'
                            'method=artist.getinfo&'
                            'artist=' + query + '&'
                            'api_key=7a17f86b00c94b16dd4d201227f7688f&'
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
    artistInfo = getArtistInfo(sys.argv[1])
    print('Name: ' + artistInfo['name'])
    print('Listeners: ' + artistInfo['listeners'])
    print('Play Count: ' + artistInfo['playcount'])
    print('Bio: ' + artistInfo['bio'])