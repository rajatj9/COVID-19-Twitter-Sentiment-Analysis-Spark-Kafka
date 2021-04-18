from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go

def plotly_wordcloud(word_frequencies):
    wc = WordCloud(stopwords=set(STOPWORDS),
                   max_words=100,
                   max_font_size=100)
    wc.generate_from_frequencies(word_frequencies)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x, y = [i[0] for i in position_list], [i[1] for i in position_list]

    freq_list = list(map(lambda k: k*1000, freq_list))
    freq_list = list(filter(lambda x: x > 1, freq_list))

    trace = go.Scatter(x=x,
                       y=y,
                       textfont=dict(size=freq_list,
                                     color=color_list),
                       hoverinfo='text',
                       hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                       mode='text',
                       text=word_list
                       )

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

    fig = go.Figure(data=[trace], layout=layout)

    return fig
