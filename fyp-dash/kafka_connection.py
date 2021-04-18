from kafka import KafkaConsumer
import json
from config import BOOTSTRAP_SERVERS, TWEETS_TOPIC, LOCATION_TOPIC, SENTIMENT_TOPIC, WORD_TOPIC, HASHTAG_TOPIC

tweet_consumer = KafkaConsumer(TWEETS_TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS,
                               value_deserializer=lambda x: json.loads(x.decode('utf-8')))

location_consumer = KafkaConsumer(LOCATION_TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS,
                                  value_deserializer=lambda x: json.loads(x.decode('utf-8')))

sentiment_consumer = KafkaConsumer(SENTIMENT_TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS,
                                   value_deserializer=lambda x: json.loads(x.decode('utf-8')))

word_consumer = KafkaConsumer(WORD_TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS,
                              value_deserializer=lambda x: json.loads(x.decode('utf-8')))

hashtag_consumer = KafkaConsumer(HASHTAG_TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS,
                                 value_deserializer=lambda x: json.loads(x.decode('utf-8')))
