FROM python:3.10-alpine

WORKDIR /app

COPY . . 

RUN pip3 install --upgrade pip
RUN pip3 install poetry

RUN poetry install 

ENV KNOT_TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDU5Mjc3NzIsImp0aSI6Ijc5N2I4MmJlLWNiMzMtNGFhNi1iYTkwLWZkOTFjNTU3NmEwNCIsImlhdCI6MTY3NDM5MTc3MiwiaXNzIjoiYWpwQGtub3Qub3JnLmJyIiwidHlwZSI6Mn0.TUu_3OJADMblSKXDMUkJu7lzVmUMkzOiNAEfBuXIQVw
ENV AMQP_URL amqp://knot:knot@192.168.1.9:5672

CMD [ "poetry", "run", "python3", "-m", "knot_protocol.main" ]