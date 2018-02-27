FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD [ "gunicorn", "--bind=0.0.0.0:80", "--workers=4", "app:app" ]
