FROM python:3.11

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt

RUN apt update && \
    apt install -y default-mysql-client

COPY scripts /scripts
RUN chmod u+x /scripts/*

COPY . /srv/root
WORKDIR /srv/root

EXPOSE 80

ENTRYPOINT ["/scripts/run-bot.sh"]
