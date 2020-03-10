
#-----------------------------------------------Libraries Used-------------------------------------------------------
import tweepy
import datetime
import time
import plotly.graph_objects as go
import operator
from opencage.geocoder import OpenCageGeocode
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
from plotly.offline import plot



key="put opencage Geocoder key"
#-----------------------------------------------Defined Functions----------------------------------------------------
def reverse_sort_dict(x):
    sorted_dict = sorted(x.items(), key=operator.itemgetter(1),reverse=True)
    return sorted_dict

def max_min_tweet(x,y):
    max_tweet=0
    min_tweet=0
    if(len(x)>20):
        max_x_key=x[0][0]
        min_x_key=x[19][0]
        max_tweet=y[max_x_key]
        min_tweet=y[min_x_key]
    else:
        n=len(x)
        max_x_key=x[0][0]
        min_x_key=x[n-1][0]
        max_tweet=y[max_x_key]
        min_tweet=y[min_x_key]
    return (max_tweet,min_tweet)
#------------------------------------------------------------------------------------------------------------------
auth = tweepy.OAuthHandler('','')
auth.set_access_token('', '')
api = tweepy.API(auth)
if (not api):
    print("Authentication failed :(")
else:
    print("Authentication successfull!!! :D")
#------------------------------------------------------------------------------------------------------------------

#-----------------------------------------Collection of Tweets-------------------------------------------------------------------------
#PART (A)
user=api.get_user('@kunalkamra88')
#user_tweets=api.user_timeline(user.id)

last_tweet_date=datetime.datetime(2020,1,25)
first_tweet_date=datetime.datetime(2018,12,1)

tweets=[]
no_of_days=420
curr=time.time()
for tweet in tweepy.Cursor(api.user_timeline,id=user.id,tweet_mode="extended").items():
    date_created=tweet.created_at
    if(date_created <= last_tweet_date):
        if(date_created >= first_tweet_date):
            tweets.append(tweet)
        else:
            break
end=time.time()
print("Time taken to fetch the tweets: {0:.2f}".format(end-curr))
print('Total number of tweets', len(tweets))
print('No of days', no_of_days)


#--------------------------------------------Collection of followers----------------------------------------------------------------------

user_followers=[]
user=api.get_user('@kunalkamra88')
cursor=tweepy.Cursor(api.followers,id=user.id,count=200).items()
while True:
    try:
        follower=cursor.next()
        user_followers.append(follower)
    except tweepy.RateLimitError:
        print("Tweepy Rate Limit Error")
        break
print('No of followers fetched:',len(user_followers))

lat=[]
long=[]
geocoder = OpenCageGeocode(key)

for user in user_followers:
    loaction= geocoder.geocode(user.location)
    if len(loaction)!=0:
        lat.append(loaction[0]['geometry']['lat'])
        long.append(loaction[0]['geometry']['lng'])

geometry = [Point(xy) for xy in zip(long, lat)]
gdf = GeoDataFrame(geometry=geometry)   

#this is a simple map that goes with geopandas
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf.plot(ax=world.plot(figsize=(10, 6)), marker='o', color='red', markersize=5)




#-------------------------------------------------  -Frequency of Tweets----------------------------------------------------------------
    
tweet_hours={'00':0,'01':0,'02':0,'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0,'16':0,'17':0,'18':0,'19':0,'20':0,'21':0,'22':0,'23':0}
tweet_days={'01':0,'02':0,'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0,'16':0,'17':0,'18':0,'19':0,'20':0,'21':0,'22':0,'23':0,'24':0,'25':0,'26':0,'27':0,'28':0,'29':0,'30':0,'31':0}
tweet_months={'Jan':0,'Feb':0,'Mar':0,'Apr':0,'May':0,'Jun':0,'Jul':0,'Aug':0,'Sep':0,'Oct':0,'Nov':0,'Dec':0}

for tweet in tweets:
    tweet_created=tweet._json['created_at']
    tweet_hours[tweet_created[11:13]]+=1
    tweet_days[tweet_created[8:10]]+=1
    tweet_months[tweet_created[4:7]]+=1
    
x=[]
y=[]
for a,b in tweet_hours.items():
    x.append(a)
    y.append(b)

scatter_graph=go.Scatter(x=x,y=y,mode='markers',marker_color=y,text='Hour, No. of Tweets')
fig = go.Figure(scatter_graph)
fig.update_layout(title='Tweet Freq w.r.t Hours')
plot(fig)
#------------------------------------------------------------------------------------------------------------------
x=[]
y=[]
for a,b in tweet_days.items():
    x.append(a)
    y.append(b)

scatter_graph=go.Scatter(x=x,y=y,mode='markers',marker_color=y,text='Day, No. of Tweets')
fig = go.Figure(scatter_graph)
fig.update_layout(title='Tweet Freq w.r.t Days')
plot(fig)
#------------------------------------------------------------------------------------------------------------------
x=[]
y=[]
for a,b in tweet_months.items():
    x.append(a)
    y.append(b)

scatter_graph=go.Scatter(x=x,y=y,mode='markers',marker_color=y,text='Month, No. of Tweets')
fig = go.Figure(scatter_graph)
fig.update_layout(title='Tweet Freq w.r.t Months')
plot(fig)

#------------------------------------------Mean Engagement Score------------------------------------------------------------------------
avg_no_tweets=len(tweets)/no_of_days
no_followers=user._json['followers_count']
tweets_score={}
for tweet in tweets:
    tweet_id=tweet._json['id_str']
    no_likes=tweet._json['favorite_count']
    no_retweets=tweet._json['retweet_count']
    score=((4*no_retweets + 2*no_likes))/no_followers
    tweets_score[tweet_id]=score
score_sum=0
for score in tweets_score.values():
    score_sum+=score
mean_score=score_sum/len(tweets_score)
# print(len(tweets_score))
print('Mean Engagement Score:',mean_score)


#------------------------------------------Top 10 Hashtags Used---------------------------------------------------
hashtags_used={}
for tweet in tweets:
    tweet_hashtags=tweet._json['entities']['hashtags']
    if(len(tweet_hashtags)!=0):
        for hashtag in tweet_hashtags:
            hashtag='#'+hashtag['text'].capitalize()
            try:
                hashtags_used[hashtag]+=1
            except:
                hashtags_used[hashtag]=1
            #print(hashtag)
            
sorted_hashtags = reverse_sort_dict(hashtags_used)
no_of_hashtags=len(sorted_hashtags)
print('No of Total Hashtags Used:-', no_of_hashtags)
print('Top 10 Hashtags Used:-')
hashtags_name=[0]*10
frq_hashtags=[0]*10
for i in range(10):
    hashtags_name[i]=sorted_hashtags[i][0]
    frq_hashtags[i]=sorted_hashtags[i][1]

fig = go.Figure([go.Bar(x=hashtags_name,y= frq_hashtags)])
fig.update_layout(title='Top 10 hashtags')
plot(fig)



#--------------------------------------Network Entity Recognition----------------------------------------------
# ORG(Oragnizations)
# PERSON
# NORP(Nationalities, Religious and Political Groups)
# WORK_OF_ART(books, song titles)
# LAW
import en_core_web_sm
nlp = en_core_web_sm.load()
bag_of_words={}
#nlp = spacy.load('en_core_web_sm')
for tweet in tweets:
    sentence=tweet._json['full_text']
    doc = nlp(sentence)
    for ent in doc.ents:
        label=ent.label_
        if(label=='ORG' or label=='PERSON' or label=='NORP' or label=='LAW' or label=='WORK_OF_ART'):
            try:
                bag_of_words[label].append(ent.text)
            except:
                bag_of_words[label]=[]
                bag_of_words[label].append(ent.text)

print(bag_of_words.keys())

#--------------------------------------Length of Tweets----------------------------------------------
len_tweets={}
for tweet in tweets:
    len_tweet=len(tweet._json['full_text'])
    try:
        len_tweets[len_tweet]+=1
    except:
        len_tweets[len_tweet]=1
x=[]
y=[]
for a,b in len_tweets.items():
    x.append(a)
    y.append(b)

scatter_graph=go.Scatter(x=x,y=y,mode='markers',marker_color=y,text='Length of tweets, No. of Tweets')
fig = go.Figure(scatter_graph)
fig.update_layout(title='Length of Tweets')
plot(fig)


#--------------------------------------------(g) part----------------------------------------------------------------------

text_tweets={}
image_tweets={}
video_tweets={}
url_tweets={}

#For Top-20
t_tweets={}
i_tweets={}
v_tweets={}
u_tweets={}

for tweet in tweets:
    
    tweet_id=tweet._json['id_str']
    tweet_entities=tweet._json['entities']
    
    text_size=tweet._json['display_text_range'][1]-tweet._json['display_text_range'][0]
    
    created_tweet={
        'created':tweet._json['created_at'],
        'no_of_likes':tweet._json['favorite_count'],
        'no_of_retweets':tweet._json['retweet_count'],
    }
    
    likes_retweets=tweet._json['favorite_count']+tweet._json['retweet_count']
    
    if(len(tweet_entities['urls'])!=0):
        no_of_urls=len(tweet_entities['urls'])
        url_sizes=0
        
        for i in range(no_of_urls):
            url_size=tweet_entities['urls'][i]['indices'][1]-tweet_entities['urls'][i]['indices'][0]
       
        if(text_size-url_size==0):
            created_tweet['no_of_urls']=tweet_entities['urls']
            url_tweets[tweet_id]=created_tweet
            u_tweets[tweet_id]=likes_retweets
    
    elif ('media' in tweet_entities.keys()):
        
        tweet_media_url=tweet_entities['media'][0]['expanded_url']
        
        created_tweet['media']=tweet_entities['media']
        
        if('video' in tweet_media_url and text_size==0):
            video_tweets[tweet_id]=created_tweet
            v_tweets[tweet_id]=likes_retweets
        
        elif('photo' in tweet_media_url and text_size==0):
            image_tweets[tweet_id]=created_tweet
            i_tweets[tweet_id]=likes_retweets
    else:
        created_tweet['text']=tweet._json['full_text']
        text_tweets[tweet_id]=created_tweet
        t_tweets[tweet_id]=likes_retweets

sorted_url_tweets=reverse_sort_dict(u_tweets)
sorted_text_tweets=reverse_sort_dict(t_tweets)
sorted_video_tweets=reverse_sort_dict(v_tweets)
sorted_image_tweets=reverse_sort_dict(i_tweets)

print('No. of Text tweets', len(text_tweets))
print('No. of Image tweets', len(image_tweets))
print('No. of Video tweets', len(video_tweets))
print('No. of Url tweets', len(url_tweets))

#------------------------------------------------------------------------------------------------------------------


max_text_tweet,min_text_tweet=max_min_tweet(sorted_text_tweets,text_tweets)
max_video_tweet,min_video_tweet=max_min_tweet(sorted_video_tweets,video_tweets)
max_image_tweet,min_image_tweet=max_min_tweet(sorted_image_tweets,image_tweets)
max_url_tweet,min_url_tweet=max_min_tweet(sorted_url_tweets,url_tweets)

max_likes=[max_text_tweet['no_of_likes'],max_video_tweet['no_of_likes'],max_image_tweet['no_of_likes'],max_url_tweet['no_of_likes']]
min_likes=[min_text_tweet['no_of_likes'],min_video_tweet['no_of_likes'],min_image_tweet['no_of_likes'],min_url_tweet['no_of_likes']]

max_retweets=[max_text_tweet['no_of_retweets'],max_video_tweet['no_of_retweets'],max_image_tweet['no_of_retweets'],max_url_tweet['no_of_retweets']]
min_retweets=[min_text_tweet['no_of_retweets'],min_video_tweet['no_of_retweets'],min_image_tweet['no_of_retweets'],min_url_tweet['no_of_retweets']]

tweets_list=['Text Tweets', 'Video Tweets', 'Image Tweets', 'Url Tweets']

fig = go.Figure(data=[
    go.Bar(name='Max No Likes', x=tweets_list, y=max_likes),
    go.Bar(name='Min No Likes', x=tweets_list, y=min_likes)
])
# Change the bar mode
fig.update_layout(barmode='group')
plot(fig)


#------------------------------------------------------------------------------------------------------------------



fig = go.Figure(data=[
    go.Bar(name='Max No Retweets', x=tweets_list, y=max_retweets),
    go.Bar(name='Min No Retweets', x=tweets_list, y=min_retweets)
])
# Change the bar mode
fig.update_layout(barmode='group')
plot(fig)


#--------------------------------------------------(c) part----------------------------------------------------------------

retweeters={}
retweets=[]
for tweet in tweets:
    try: 
        for retweet in api.retweets(tweet.id,100):
            retweets.append(retweet)
            user_name=retweet.user.screen_name
            if user_name in retweeters.keys():
                retweeters[user_name]+=1
            else:
                retweeters[user_name]=1
    except tweepy.RateLimitError:
        print("Tweepy Rate Limit Error")
        break


#------------------------------------------------------------------------------------------------------------------

sorted_retweeters = sorted(retweeters.items(), key=operator.itemgetter(1),reverse=True)
Top_10=sorted_retweeters[:10]
Top_10_Profiles=[0]*10
Top_10_Profiles_no_followers=[0]*10
followers_of_top10=[0]*10
following_of_top10=[0]*10
statuses_of_Top_10=[0]*10
for i in range(10):
    Top_10_Profiles_no_followers[i]=Top_10[i][1]
    Top_10_Profiles[i]=Top_10[i][0]
    
    user = api.get_user(Top_10_Profiles[i])
    statuses_of_Top_10[i]=user.statuses_count
    followers_of_top10[i]=user.followers_count
    following_of_top10[i]=user.friends_count
    
scatter_graph=go.Scatter(x=followers_of_top10,y=following_of_top10, mode="markers+text",text=Top_10_Profiles)
fig = go.Figure(scatter_graph)

fig.update_layout(title='Followers/Following')
plot(fig)


#------------------------------------------------------------------------------------------------------------------

fig = go.Figure([go.Bar(x=Top_10_Profiles,y= Top_10_Profiles_no_followers)])
fig.update_layout(title='No of RT')
plot(fig)

#------------------------------------------------------------------------------------------------------------------
retweets_by_Top_10=[]
for retweet in retweets:
    if retweet.user.screen_name in Top_10_Profiles:
            retweets_by_Top_10.append(retweet)

#tweet_hours={'00':0,'01':0,'02':0,'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0,'16':0,'17':0,'18':0,'19':0,'20':0,'21':0,'22':0,'23':0}
tweet_days={'01':0,'02':0,'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0,'16':0,'17':0,'18':0,'19':0,'20':0,'21':0,'22':0,'23':0,'24':0,'25':0,'26':0,'27':0,'28':0,'29':0,'30':0,'31':0}
#tweet_months={'Jan':0,'Feb':0,'Mar':0,'Apr':0,'May':0,'Jun':0,'Jul':0,'Aug':0,'Sep':0,'Oct':0,'Nov':0,'Dec':0}

for tweet in retweets_by_Top_10:
    tweet_created=tweet._json['created_at']
    #tweet_hours[tweet_created[11:13]]+=1
    tweet_days[tweet_created[8:10]]+=1
    #tweet_months[tweet_created[4:7]]+=1
    
x=[]
y=[]
for a,b in tweet_days.items():
    x.append(a)
    y.append(b)

scatter_graph=go.Scatter(x=x,y=y,mode='markers',marker_color=y,text='Days, No. of RT')
fig = go.Figure(scatter_graph)
fig.update_layout(title='RT Freq w.r.t Days')
plot(fig)

#------------------------------------------------------------------------------------------------------------------


fig = go.Figure([go.Bar(x=Top_10_Profiles,y= statuses_of_Top_10)])
fig.update_layout(title='No of Statuses')
plot(fig)

#--------------------------------------(c) part geolocaton----------------------------------------------------------------------------

Lat_of_Top_10=[]
Long_of_Top_10=[]
geocoder = OpenCageGeocode(key)
for i in range(10):
    user = api.get_user(Top_10_Profiles[i])
    loaction= geocoder.geocode(user.location)
    if len(loaction)!=0:
        Lat_of_Top_10.append(loaction[0]['geometry']['lat'])
        Long_of_Top_10.append(loaction[0]['geometry']['lng'])
        
        


geometry = [Point(xy) for xy in zip(Long_of_Top_10, Lat_of_Top_10)]
gdf = GeoDataFrame(geometry=geometry)   

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf.plot(ax=world.plot(figsize=(10, 6)), marker='o', color='red', markersize=15)

    
 
