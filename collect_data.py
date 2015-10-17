__author__ = 'wanyanxie'


from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import re
import sys
import json
import dateutil.parser
from pytz import timezone
import pytz
import tweepy
import time
import urllib3
import random
import csv
import os

#Listener Class Override
class listener(StreamListener):

      def __init__(self, start_time, time_limit):

          self.time = start_time
          self.limit = time_limit
          self.lastID = None
          #self.regex = re.compile('|'.join(keywords).lower())


      def on_data(self, data):
         # print time.time() - self.time
          while (time.time() - self.time) < self.limit:
              try:
                  tweet = json.loads(data)

                  if not tweet.has_key('id_str'):
                     #print 'No tweet ID - ignoring tweet.'
                     return True

                  #### ignore duplicates tweets
                  tweetID = tweet['id_str']
                  if tweetID != self.lastID:
                     self.lastID = tweet['id_str']
                  else:
                     return True

                  if not tweet.has_key('user'):
                     #print 'No user data - ignoring tweet.'
                     return True
                  user = tweet['user']['name']
                  text = parse_text(tweet['text'])
                  print text

           #       print user, text


                  ### mathces the key words
                  # matches = re.search(self.regex, text.lower())
                  # if not matches:
                  #     return True

                  #### remove the retweets
                  # if tweet['retweeted'] or 'RT @'  in tweet['text']:
                  #     return True

                  location = tweet['user']['location']
                  source = tweet['source']

                  d = dateutil.parser.parse(tweet['created_at'])
                  d_tz = pytz.timezone('UTC').normalize(d)
                  localtime = d.astimezone(timezone('US/Pacific'))
                  tmstr = localtime.strftime("%Y%m%d-%H:%M:%S")
                  #print tweetID, text

                  # saveFile = open('raw_tweets.json', 'a')
                  # saveFile.write(data)
                  # saveFile.write('\n')
                  # saveFile.close()

                  # append the hourly tweet file
                  with open('./data/tweets-%s.data' % tmstr.split(':')[0], 'a+') as f:
                       f.write(data)

                  geo = tweet['geo']
                  if geo and geo['type'] == 'Point':
                     coords = geo['coordinates']
                  else:
                      return True

                  #
                  with open('./data/data_geo.txt', 'a+') as f:
                       #f.write('tweetID,creat_time,Coord1,Coord2,Text')
                       print("%s,%s,%f,%f,%s" % (tweetID,tmstr,coords[0],coords[1],text))
                       f.write("%s,%s,%f,%f,%s\n" % (tweetID,tmstr,coords[0],coords[1],text))



              except BaseException, e:
                  print 'failed ondata,', str(e)
                  time.sleep(5)
                  pass

              except urllib3.exceptions.ReadTimeoutError, e:
                  print 'failed connection,', str(e)
                  time.sleep(5)
                  pass

          exit()



      def on_error(self, status):
          print "error_message:", status

def parse_text(text):
    """
    Read an txt file
    Replace numbers, punctuation, tab, carriage return, newline with space
    Normalize w in wordlist to lowercase
    """
    text = text.encode('latin1', errors='ignore')
    #text = text.rstrip('\n')
    text = text.replace('\n', ' ')
    return text



def read_csv(file):
    data = []
    with open(file) as f:
        for line in f:
            data.append(line.strip('\n').lower())
    return data

def OAuth(consumer_key, consumer_secret, access_token, access_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    try:
        redirect_url = auth.get_authorization_url()
        print redirect_url
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
    api = tweepy.API(auth)
    print api.me().name
    return auth


def main():
    consumer_key = '7z0EH9KkaJOrMzzByX1KvZasd'
    consumer_secret = 'AQ6wVGxj4sOLZJvtrIk7spX4STYyYoxYSSHVk81saoSWEQtjqB'
    access_token = '1705070078-VqlcsHdn7Rz1RrXpB4ACn249g05NwgMI1fixNc8'
    access_secret = '6qaVRAmCnVuJPcPJrxA0RlpmkCcGE6pJHq2HgdsJ1FWIo'
    auth = OAuth(consumer_key, consumer_secret, access_token, access_secret)


    start_time = time.time() #grabs the system time
    time_limit = 10000
    keywords = read_csv('candidates.txt')
    print keywords

    #keywords = ["happy", "sad"]
   # print '|'.join(keywords).lower()
   # keyword_list = random.sample(keywords, 300) #track list
    #keyword_list = [keywords[i] for i in range(400)]
    #print keyword_list

    #keywords = ['traffic, accident, disabled vehicle, warning, emergency']
    dir = 'data'
    if not os.path.exists(dir):
       os.makedirs(dir)

    twitterStream = Stream(auth, listener(start_time, time_limit))
    twitterStream.filter(track = keywords, languages=['en'])

if __name__ == '__main__':
    main()
