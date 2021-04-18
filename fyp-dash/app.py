import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from datetime import datetime, timedelta
import rx
import rx.operators as op
from config import UPDATE_FREQUENCY_SECONDS, MAX_SIZE
from kafka_connection import tweet_consumer, location_consumer, hashtag_consumer, word_consumer, sentiment_consumer
from utils import get_updated_cache_value
from plotly_wordcloud import plotly_wordcloud
from layout import data_table, generate_card, generate_bar_chart, navbar, generate_pie_chart, \
    generate_card_with_two_charts
from style import CONTENT_STYLE

data_cache = []
chart_data = {
    'location_data': {},
    'sentiment_data': {},
    'word_data': {},
    'hashtag_data': {},
    'wordcloud': None,
    'hashtag_bar_chart': ([], []),
    'sentiment_bar_chart': None,
    'sentiment_pie_chart': None
}


def update_tweet_cache():
    start = datetime.now()
    print("Starting updating of cache")
    try:
        new_data = tweet_consumer.poll(max_records=int(MAX_SIZE / 2))
        new_records = []
        for tp in new_data:
            records = new_data[tp]
            records = list(map(lambda x: x.value, records))
            print("NEW TWEET RECORDS:", records)
            for record in records:
                record['dashboard_time'] = str(datetime.now().strftime('%H:%M:%S'))
                record['fetched_at'] = record['fetched_at'].split('T')[1]
                record['polarity'] = round((0.5 - record['polarity'])/0.5, 2)
            print("RECORDS AFTER ADDING dashboard_time:", records)
            new_records = new_records + records
    except Exception as e:
        print(f"Failed fetching data from Consumer: {e}")
        return
    print("Finished fetching data.\nTime for fetching data: ", datetime.now() - start)
    global data_cache
    data_cache = new_records + data_cache[:(MAX_SIZE - len(new_records)):] \
        if len(data_cache) + len(new_records) > MAX_SIZE else new_records + data_cache
    return


def update_chart_data_cache():
    start = datetime.now()
    print("Started updating chart data cache")
    try:
        global chart_data
        chart_data['location_data'] = get_updated_cache_value(location_consumer, chart_data, 'location_data', 100)
        chart_data['hashtag_data'] = get_updated_cache_value(hashtag_consumer, chart_data, 'hashtag_data', 100)
        chart_data['sentiment_data'] = get_updated_cache_value(sentiment_consumer, chart_data, 'sentiment_data', 5)
        chart_data['word_data'] = get_updated_cache_value(word_consumer, chart_data, 'word_data', 100)
        before_word_cloud_time = datetime.now()
        chart_data['wordcloud'] = plotly_wordcloud(chart_data['word_data'])
        after_word_cloud_time = datetime.now()
        print("Time for generating wordcloud: ", after_word_cloud_time - before_word_cloud_time)
        chart_data['hashtag_bar_chart'] = generate_bar_chart(chart_data['hashtag_data'])
        print("Time for generating hashtag_bar_chart: ", datetime.now() - after_word_cloud_time)
        chart_data['sentiment_bar_chart'] = generate_bar_chart(chart_data['sentiment_data'])
        print(f"Finished updating chart data cache in {datetime.now() - start}")
        chart_data['sentiment_pie_chart'] = generate_pie_chart(chart_data['sentiment_data'])
    except Exception as e:
        print(f"Failed fetching chart data: {e}")


def update_tweet_cache_observable(observer, scheduler='not_set'):
    update_tweet_cache()
    observer.on_completed()
    return

def update_chart_data_cache_observable(observer, scheduler='not_set'):
    update_chart_data_cache()
    observer.on_completed()
    return


rx.interval(timedelta(seconds=UPDATE_FREQUENCY_SECONDS)).pipe(
    op.map(lambda _: rx.create(update_tweet_cache_observable)),
    op.merge(max_concurrent=1)
).subscribe()


rx.interval(timedelta(seconds=UPDATE_FREQUENCY_SECONDS*2.5)).pipe(
    op.map(lambda _: rx.create(update_chart_data_cache_observable)),
    op.merge(max_concurrent=1)
).subscribe()

def get_data():
    return data_cache

def get_chart_data():
    return chart_data


tweet_content = html.Div(id='tweet-content')
wordcloud_component = generate_card("Wordcloud", dcc.Graph(id='wordcloud-component'))
hashtag_bar_chart = generate_card("Most Popular Hashtags", dcc.Graph(id='hashtag-bar-chart'))
sentiment_bar_chart = generate_card_with_two_charts("Sentiment Breakdown", [dcc.Graph(id='sentiment-bar-chart'),
                                                            dcc.Graph(id='sentiment-pie-chart')])

content = html.Div(id='page-content', children=[tweet_content, data_table, wordcloud_component,
                                                hashtag_bar_chart, sentiment_bar_chart], style=CONTENT_STYLE)
interval = dcc.Interval(id='interval-component', interval=UPDATE_FREQUENCY_SECONDS * 1000, n_intervals=0)
location = dcc.Location(id='url')


app = dash.Dash(external_stylesheets=[dbc.themes.LUMEN])
app.layout = html.Div([
    location,
    navbar,
    content,
    interval
])

@app.callback(
    Output('tweet-table', 'data'),
    Output('wordcloud-component', 'figure'),
    Output('hashtag-bar-chart', 'figure'),
    Output('sentiment-bar-chart', 'figure'),
    Output('sentiment-pie-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_frontend(_):
    return get_data(), chart_data['wordcloud'], chart_data['hashtag_bar_chart'], chart_data['sentiment_bar_chart'], \
           chart_data['sentiment_pie_chart']


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)
