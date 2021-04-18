from __future__ import print_function

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from subprocess import call
import json
import sys
from datetime import datetime

dependencies = ['kafka-python', 'numpy', 'pandas', 'requests']
for package in dependencies:
    call([sys.executable, '-m', 'pip', 'install', package])

from kafka import KafkaProducer

bootstrap_servers_str = '10.244.1.24:9092,10.244.3.16:9092,10.244.1.25:9092'
bootstrap_servers = ['10.244.1.24:9092', '10.244.3.16:9092', '10.244.1.25:9092']
topic = 'test'

stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
              'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
              'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
              'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were',
              'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
              'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
              'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
              'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
              'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
              'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
              'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain',
              'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
              "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
              "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
              'wouldn', "wouldn't"}

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)


def cleaner(tweet):
    import re
    tweet = re.sub("@[A-Za-z0-9]+", "", tweet)
    tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet)
    tweet = tweet.replace("#", "").replace("_", " ")
    tweet = tweet.replace("RT", "")
    return tweet


def handler(message):
    records = message.collect()
    for record in records:
        producer.send('result', json.dumps(record).encode('utf-8'))
        producer.flush()
    print("Messages sent to Kafka.")


def find_sentiment(polarity):
    if polarity > 0.5:
        return 'Negative'
    elif polarity < 0.5:
        return 'Positive'
    return 'Neutral'

def transform_tweet_data(tweet_record):
    tweet = tweet_record['text']
    tweet_length = len(tweet)
    tweet_polarity = tweet_record['polarity']
    tweet_sentiment = find_sentiment(tweet_polarity)
    data = {'tweet': tweet, 'length': tweet_length, 'polarity': tweet_polarity, 'sentiment': tweet_sentiment,
            'recv_time': str(datetime.now()), 'fetched_at': tweet_record['fetched_at']}
    return data


def send_data(rdd, topic_name):
    now = datetime.now()
    data_array = rdd.collect()
    collection_time = datetime.now()
    print("Time for collection in RDD: ", collection_time - now)
    response = {'data': data_array}
    producer.send(topic_name, json.dumps(response).encode('utf-8'))
    print("Time for sending to Kafka Topic: ", datetime.now() - collection_time)
    print(f"Sent to topic {topic_name}:", data_array)


def update_func(value, last_sum):
    return value + (last_sum or 0)


if __name__ == "__main__":
    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
    ssc = StreamingContext(sc, 0.8)
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": bootstrap_servers_str})

    lines = kvs.map(lambda x: x[1])
    tweet_records = lines.map(lambda x: json.loads(x))

    word_counts = tweet_records.flatMap(lambda record: cleaner(record['text']).split(" ")). \
        filter(lambda word: word not in stop_words) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(update_func).foreachRDD(lambda rdd: send_data(rdd, 'word_counts'))

    hashtag_count = tweet_records.flatMap(lambda record: record['hashtags']).filter(lambda x: x != 'COVID19'). \
        map(lambda tag: (tag, 1)). \
        reduceByKey(update_func).foreachRDD(lambda rdd: send_data(rdd, 'hashtag_counts'))

    location_count = tweet_records.flatMap(lambda record: [record['user_location']]).map(lambda location: (location, 1)) \
        .reduceByKey(update_func).foreachRDD(lambda rdd: send_data(rdd, 'location_counts'))

    sentiments = tweet_records.flatMap(lambda record: [record['polarity']]).map(find_sentiment).map(
        lambda sentiment: (sentiment, 1)).reduceByKey(update_func) \
        .foreachRDD(lambda rdd: send_data(rdd, 'sentiment_counts'))

    tweet_records.map(transform_tweet_data).foreachRDD(lambda x: handler(x))

    ssc.start()
    ssc.awaitTermination()
