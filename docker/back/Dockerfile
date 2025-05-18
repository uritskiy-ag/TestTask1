FROM python:3.12
USER root
WORKDIR /code/app

COPY ./requirements.txt /code/app
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

