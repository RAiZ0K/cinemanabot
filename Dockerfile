FROM python:3.10-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py /usr/src/app/

ENV TG_BOT_TOKEN ''
ENV TG_BOT_NAME 'uz_ticket_bot'
ENV SCAN_DELAY_SEC 60
ENV STATSD_HOST ''
ENV STATSD_PORT 8125

CMD [ "python", "bot.py" ]
