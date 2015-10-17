__author__ = 'wanyanxie'
import tweepy
import time
import os
import sys
import json
import argparse

FOLLOWING_DIR = 'following'
USERS_DIR = 'twitter-users'

MAX_FRIENDS = 200
FRIENDS_OF_FRIENDS_LIMIT = 200

if not os.path.exists(FOLLOWING_DIR):
    os.makedirs(FOLLOWING_DIR)

if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)


enc = lambda x: x.encode('ascii', errors='ignore')

consumer_key = '7z0EH9KkaJOrMzzByX1KvZasd'
consumer_secret = 'AQ6wVGxj4sOLZJvtrIk7spX4STYyYoxYSSHVk81saoSWEQtjqB'
access_token = '1705070078-VqlcsHdn7Rz1RrXpB4ACn249g05NwgMI1fixNc8'
access_secret = '6qaVRAmCnVuJPcPJrxA0RlpmkCcGE6pJHq2HgdsJ1FWIo'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)


def get_follower_ids(twitter_user_id, max_depth=1, current_depth=0, taboo_list=[]):

    # print 'current depth: %d, max depth: %d' % (current_depth, max_depth)
    # print 'taboo list: ', ','.join([ str(i) for i in taboo_list ])

    if current_depth == max_depth:
        print 'out of depth'
        return taboo_list

    if twitter_user_id in taboo_list:
        # we've been here before
        print 'Already been here.'
        return taboo_list
    else:
        taboo_list.append(twitter_user_id)

    try:
        userfname = os.path.join('twitter-users', str(twitter_user_id) + '.json')
        if not os.path.exists(userfname):
            print 'Retrieving user details for twitter id %s' % str(twitter_user_id)
            while True:
                try:
                    user = api.get_user(twitter_user_id)

                    d = {'name': user.name,
                         'screen_name': user.screen_name,
                         'id': user.id,
                         'friends_count': user.friends_count,
                         'followers_count': user.followers_count,
                         'followers_ids': user.followers_ids()}
                    with open(userfname, 'w') as outf:
                        outf.write(json.dumps(d, indent=1))



                    user = d
                    break
                except tweepy.TweepError, error:
                    print type(error)

                    if str(error) == 'Not authorized.':
                        print 'Can''t access user data - not authorized.'
                        return taboo_list

                    if str(error) == 'User has been suspended.':
                        print 'User suspended.'
                        return taboo_list

                    errorObj = error[0][0]

                    print errorObj

                    if errorObj['message'] == 'Rate limit exceeded':
                        print 'Rate limited. Sleeping for 15 minutes.'
                        time.sleep(15 * 60 + 15)
                        continue

                    return taboo_list
        else:
            user = json.loads(file(userfname).read())

        screen_name = enc(user['screen_name'])
        fname = os.path.join(FOLLOWING_DIR, screen_name + '.csv')
        friendids = []
        # only retrieve friends of TED... screen names
        if True:
        #if screen_name.startswith('TED'):
            if not os.path.exists(fname):
                print 'No cached data for known screen name "%s"' % screen_name
                with open(fname, 'w') as outf:
                    params = (enc(user['name']), screen_name)
                    print 'Retrieving friends for user "%s" (%s)' % params

                    # page over friends
                    c = tweepy.Cursor(api.friends, id=user['id']).items()

                    friend_count = 0
                    while True:
                        try:
                            friend = c.next()
                            friendids.append(friend.id)
                            params = (friend.id, enc(friend.screen_name), enc(friend.name))
                            outf.write('%s\t%s\t%s\n' % params)
                            friend_count += 1
                            if friend_count >= MAX_FRIENDS:
                                print 'Reached max no. of friends for "%s".' % friend.screen_name
                                break
                        except tweepy.TweepError:
                            # hit rate limit, sleep for 15 minutes
                            print 'Rate limited. Sleeping for 15 minutes.'
                            time.sleep(15 * 60 + 15)
                            continue
                        except StopIteration:
                            break
            else:
                friendids = [int(line.strip().split('\t')[0]) for line in file(fname)]

            print 'Found %d friends for %s' % (len(friendids), screen_name)

            # get friends of friends
            cd = current_depth
            if cd+1 < max_depth:
                for fid in friendids[:FRIENDS_OF_FRIENDS_LIMIT]:
                    taboo_list = get_follower_ids(fid, max_depth=max_depth,
                        current_depth=cd+1, taboo_list=taboo_list)

            if cd+1 < max_depth and len(friendids) > FRIENDS_OF_FRIENDS_LIMIT:
                print 'Not all friends retrieved for %s.' % screen_name

    except Exception, error:
        print 'Error retrieving followers for user id: ', twitter_user_id
        print error

        if os.path.exists(fname):
            os.remove(fname)
            print 'Removed file "%s".' % fname

        sys.exit(1)

    return taboo_list



if __name__ == '__main__':
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-s", "--screen-name", required=True, help="Screen name of twitter user")
    # ap.add_argument("-d", "--depth", required=True, type=int, help="How far to follow user network")
    # args = vars(ap.parse_args())
    #
    # twitter_screenname = args['screen_name']
    # depth = int(args['depth'])

   # twitter_screenname = 'YouTube'
    twitter_screenname = 'usfca_analytics'
   # twitter_screenname = 'TheAS'


    depth = 2


    if depth < 1 or depth > 3:
        print 'Depth value %d is not valid. Valid range is 1-3.' % depth
        sys.exit('Invalid depth argument.')

    print 'Max Depth: %d' % depth
    matches = api.lookup_users(screen_names=[twitter_screenname])

    if len(matches) == 1:
        print get_follower_ids(matches[0].id, max_depth=depth)
    else:
        print 'Sorry, could not find twitter user with screen name: %s' % twitter_screenname