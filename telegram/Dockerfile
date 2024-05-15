FROM python:3.11-slim

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ../requirements.txt .
RUN pip install -r requirements.txt

COPY .. /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 5000

ENTRYPOINT ["python", "telegram/tg_bot.py"]
