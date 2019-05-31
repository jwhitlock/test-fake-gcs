FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client-test.py fake_client.py ./
CMD [ "python", "./client-test.py" ]
