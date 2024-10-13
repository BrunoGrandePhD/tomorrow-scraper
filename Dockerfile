FROM python:3.11.7@sha256:63bec515ae23ef6b4563d29e547e81c15d80bf41eff5969cb43d034d333b63b8

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install cron
RUN apt-get update \
    && apt-get install -y cron \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt

COPY ./tomorrow /app/tomorrow
COPY ./tomorrow-cron /etc/cron.d/tomorrow-cron

ADD ./command.sh /app/command.sh
RUN chmod +x /app/command.sh

ADD ./tomorrow-cron /app/tomorrow-cron
RUN crontab /app/tomorrow-cron
