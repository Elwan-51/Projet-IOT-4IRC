
FROM python:3.11


WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./config.json /code/config.json

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "app/log.ini"]


