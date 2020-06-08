FROM ubuntu:18.04

LABEL Author="Vivek Kumar"
LABEL E-mail="kumarvivek.9097@gmail.com"
LABEL version="0.0.1b"

RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-pip python3-dev build-essential python3-virtualenv

COPY . /app
#COPY ./requirements.txt /app
WORKDIR /app

# Install dependencies:
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000
ENTRYPOINT [ "python3" ]

# Run the application:
CMD [ "app.py" ]
