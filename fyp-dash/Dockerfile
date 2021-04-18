FROM python:3.7
COPY requirements.txt /app/
COPY app.py /app/
COPY config.py /app/
COPY kafka_connection.py /app/
COPY plotly_wordcloud.py /app/
COPY style.py /app/
COPY layout.py /app/
COPY utils.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8050
CMD python -u app.py

