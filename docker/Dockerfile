FROM python:3.10-alpine

WORKDIR /app

COPY . . 

RUN pip3 install --upgrade pip
RUN pip3 install poetry

RUN poetry install 

ENV KNOT_TOKEN ""
ENV AMQP_URL ""

CMD [ "poetry", "run", "python3", "-m", "knot_protocol.main" ]