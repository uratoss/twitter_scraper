# !/usr/bin/env python
import tweepy
import datetime
from datetime import timedelta
import sys
import os
import time
import json
import argparse

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('account_id',help ='screen name that you want to scrapping')
    parser.add_argument('-o','--out_path',default='./',help='output path of precessed file')
    args = parser.parse_args()

    account=args.account_id
    secret_file = json.load(open('secret.json','r'))

    consumer_key = secret_file["consumer"]["key"]
    consumer_secret = secret_file["consumer"]["secret"]
    access_token = secret_file["access_token"]["key"]
    access_token_secret = secret_file["access_token"]["secret"]
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    ids_file = json.load(open('ids.json','r'))
    since_id = ids_file["since_id"]
    max_id = ids_file["max_id"]

    if max_id is 0:
        ids_file["max_id"] = max_id = api.user_timeline(account,count=1)[0].id
    
    out_path = args.out_path
    date = datetime.datetime.today()
    folder_name = "_".join([str(date.year), str(date.month), str(date.day)])
    out_path = (
        os.path.join(out_path, folder_name) + os.sep
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    max_id+=1
    while 1:
        tweets=api.user_timeline(account,max_id = max_id-1,count=200)
        for tweet in tweets:
            # save max_id
            ids_file["max_id"] = max_id = tweet.id
            json.dump(ids_file,open('ids.json','w'))
            
            tweet = api.get_status(tweet.id,tweet_mode='extended')
            tweet.created_at+=timedelta(hours=9)
            date = tweet.created_at
            tweet_text = tweet.full_text.replace('\n','<nn>').strip().split()
            if tweet_text[0].startswith('@'):
                tweet_text.pop(0)
            tweet_text = ''.join(tweet_text)
            if (not tweet.entities['urls']==[]):
                continue
            if ('media' in tweet.entities):
                continue
            if tweet_text.startswith('RT'):
                continue

            for tag in tweet.entities['hashtags']:
                tweet_text = tweet_text.replace('#'+tag['text'],'') #ハッシュタグを消す
            for user in tweet.entities['user_mentions']:
                tweet_text = tweet_text.replace('@'+user['screen_name'],'') #名前をけす

            print('=========================================') # 見やすいように
            print(tweet.created_at+timedelta(hours=9))
            print(tweet_text) #各ツイート内容表示
            sequence_path = os.path.join(out_path,'sequence.txt')
            with open(sequence_path,mode='a') as f:
                print(tweet_text,end='\n',file=f)
        time.sleep(200)

if __name__ == '__main__':
    main()
