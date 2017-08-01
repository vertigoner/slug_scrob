import sys
import os

sys.path.append(os.path.abspath('./../config'))

from env import *
from lastfm import *

if __name__ == '__main__':
   
    lfm = lastfm()

    lfm.scrobble(sys.argv[1], sys.argv[2])

    artistInfo = lfm.getArtistInfo(sys.argv[1])
    print()
    print('Name: ' + artistInfo['name'])
    print('Listeners: ' + artistInfo['listeners'])
    print('Play Count: ' + artistInfo['playcount'])
    print('Bio: ' + artistInfo['bio'])