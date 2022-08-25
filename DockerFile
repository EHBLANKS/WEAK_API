FROM python:3.10-slim

WORKDIR /

RUN apt-get update -y \
    && apt-get install libpq-dev gcc -y \
    && rm -rf /var/lib/apt/lists/* 

RUN pip install --upgrade pip

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Now copy the code, so that we use dockers caching in prev steps to speed up the build
COPY ./api /api

# Copy the default enivronment variables to the docker container
# This will allow us to connect the firebase container to Firebase and our other online services
COPY ./default.env /.env

EXPOSE 80

CMD ["gunicorn", "--workers", "4", "-k", "uvicorn.workers.UvicornWorker", "api.main:app", "--bind", "0.0.0.0:9001"]

