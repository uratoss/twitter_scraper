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
    num = 0
    while 1:
        tweets=api.user_timeline(account,max_id = max_id-1,count=200)
        num+=200
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
            replied_id = tweet.in_reply_to_status_id
            try:
                reply = api.get_status(replied_id,tweet_mode='extended')
            except:
                print('Error')
                continue
            if (not tweet.entities['urls']==[] ) or (not reply.entities['urls'] ==[]):
                continue
            if ('media' in tweet.entities) or ('media' in reply.entities):
                continue
            print(reply.full_text)

            reply_text = ''.join(reply.full_text.replace('\n','<nn>').strip().split())
            for tag in reply.entities['hashtags']:
                reply_text = reply_text.replace('#'+tag['text'],'') #ハッシュタグを消す
            for user in reply.entities['user_mentions']:
                reply_text = reply_text.replace('@'+user['screen_name'],'') #名前をけす
            if reply_text == '' or tweet_text == '' :
                continue

            for tag in tweet.entities['hashtags']:
                tweet_text = tweet_text.replace('#'+tag['text'],'') #ハッシュタグを消す
            for user in tweet.entities['user_mentions']:
                tweet_text = tweet_text.replace('@'+user['screen_name'],'') #名前をけす

            print('=========================================') # 見やすいように
            print(reply.user.name)
            print(reply_text) #各ツイート内容表示
            print('----------------------------------------') # 見やすいように
            print(date) #書くツイートの投稿時間表示
            print(tweet_text) #各ツイート内容表示
            req_path = os.path.join(out_path,'req.txt')
            with open(req_path,mode='a') as f:
                print(reply_text,end='\n',file=f)
            res_path = os.path.join(out_path,'res.txt')
            with open(res_path,mode='a') as f:
                print(tweet_text,end='\n',file=f)
        if(num >= 3600):
            break
        time.sleep(400)

if __name__ == '__main__':
    main()
