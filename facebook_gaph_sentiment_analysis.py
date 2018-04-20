#translator to translate comments from others languages to english
from  translate import Translator

import requests
import signal
import sys
import pprint
graph_api_version = 'v2.9'

# add your token instead
access_token = access_token
translator= Translator(to_lang="fr")

# the user id for me the facebook page of GOAL  ENGLISH
user_id = '25427813597'
limit = 200
posts = []
url_profile = 'https://graph.facebook.com/{}/{}?fields=feed'.format(graph_api_version,user_id)

r_profile = requests.get(url_profile, params={'access_token': access_token})
while True:
    data = r_profile.json()
    feed = data['feed']
    for post in feed['data']:
        posts.append(post['id'])
    if 0 < limit <= len(posts):
        break
    if 'paging' in data and 'next' in data['paging']:
        r_profile = requests.get(data['paging']['next'])
    else:
        break

comments = []


post_index = 0
for post in posts :
    url = 'https://graph.facebook.com/{}/{}/comments'.format(graph_api_version,post)
    r = requests.get(url, params={'access_token': access_token})
    print('post Number :',post_index=+1)
    while True:
        data = r.json()

        # catch errors returned by the Graph API
        if 'error' in data:
            raise Exception(data['error']['message'])

        # append the text of each comment into the comments list
        for comment in data['data']:
            # remove line breaks in each comment
            text = comment['message'].replace('\n', ' ')

            #translate the comments to english before add them
            text = translator.translate(text)
            comments.append(text)

        print('Got {} comments, total: {}'.format(len(data['data']), len(comments)))

        # check if we have enough comments
        if 0 < limit <= len(comments):
            break

        # check if there are more comments
        if 'paging' in data and 'next' in data['paging']:
            r = requests.get(data['paging']['next'])
        else:
            break


#sentiment analysis part
from nltk.sentiment  import vader
sid = vader.SentimentIntensityAnalyzer()

output = [{ 'sentence' :sentence , 'scores' : sid.polarity_scores(sentence) } for sentence in comments ]
import json
sentiment_analysis = open('sentiment_analysis_'+user_id+'_en.json','w')
json_out = json.dump(output,sentiment_analysis)
pprint.pprint(json_out)

import pandas as pd
import numpy as np
df = pd.read_json('sentiment_analysis_'+user_id+'_en.json').fillna(' ')

# the mean of sentiment in a dataframe contains comments
def mean_senti(df) :
    neg = []
    pos = []
    neutre = []
    for e in df["scores"] :
        neg.append(e["neg"])
        pos.append(e["pos"])
        neutre.append(e["neu"])
    neg = np.array(neg)
    pos = np.array(pos)
    neut = np.array(neutre)
    neutre = np.mean(neut, axis=0)
    positive = np.mean(pos, axis=0)
    negative = np.mean(neg, axis=0)
    return(negative,positive,neutre)

#make a sub dataframe of comments contains the term "zidan"
sub_def = df[df['sentence'].str.contains("zidan")]

(neg_c,pos_c,neutre_c) = mean_senti(sub_def)
print('negative :',neg_c,'positive :',pos_c,'neutre :',neutre_c)
