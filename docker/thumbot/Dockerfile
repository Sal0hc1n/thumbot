FROM frolvlad/alpine-python-machinelearning

RUN apk add --update alpine-sdk
RUN apk add python3-dev libxslt-dev

COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt

# copy over our app code
ADD ./src /src
WORKDIR /src

CMD ["python", "main.py"]
