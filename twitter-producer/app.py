import json
import tweepy
from datetime import datetime
from kafka import KafkaProducer
import joblib

# bootstrap_servers = ['localhost:9092']

# Define topic name where the message will publish
topicName = 'test'
model = joblib.load('./filename.pkl')

# Initialize producer variable


# Note: Some of the imports are external python libraries. They are installed on the current machine.
# If you are running multinode cluster, you have to make sure that these libraries
# and currect version of Python is installed on all the worker nodes.

class TweeterStreamListener(tweepy.StreamListener):
    """ A class to read the twitter stream and push it to Kafka"""

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.producer = KafkaProducer(bootstrap_servers = ["10.244.1.24:9092","10.244.3.16:9092","10.244.1.25:9092"])

    def on_status(self, status):
        """ This method is called whenever new data arrives from live stream.
        We asynchronously push this data to kafka queue"""
        msg =  status.text
        polarity = list(list(model.predict_proba([msg]))[0])[1]
        created_at = str(status.created_at)
        fetched_at = datetime.now().isoformat()
        geo = status.geo['coordinates'] if status.geo is not None else None
        coordinates = status.coordinates
        place = status.place
        hashtags = list(map(lambda x : x['text'], dict(status.entities)['hashtags']))
        user_location = status.user.location
        data = { 'text': msg, 'created_at': created_at, 'fetched_at': fetched_at, 'geo': geo, 'coordinates': coordinates, 'hashtags': hashtags, 'user_location': user_location, 'polarity': polarity }
        encoded_string_data = json.dumps(data).encode('utf-8')
        try:
            print("Sending message to Kafka Queue: ", encoded_string_data)
            self.producer.send('test', encoded_string_data)
            self.producer.flush()
        except Exception as e:
            print(e)
            return False
        return True

    def on_error(self, status_code):
        print("Error received in kafka producer", status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        return True # Don't kill the stream

if __name__ == '__main__':
    consumer_key = "rdk7FzlvvHm6VzhpOoPtLgYDK"
    consumer_secret = "2ToRQMFpydlvXgdbczByyybWpmHymJ9ZyN4ROaKjwxYVORX8aX"
    access_key = "1307657043520622592-HkuG4BvjzO713FzU7fCndqjobTpK6E"
    access_secret = "Zfs1c3Sy2KOpmTg7RBsbaltg4AKuh8Oq0Z7nElNQyFmZD"


    # Create Auth object
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # Create stream and bind the listener to it
    stream = tweepy.Stream(auth, listener = TweeterStreamListener(api))

    #Custom Filter rules pull all traffic for those filters in real time.
    stream.filter(track = ['covid19'], languages = ['en'])
#     stream.filter(locations=[-180,-90,180,90], languages = ['en'])
    
