FROM python:3.8.5

# FIX DEPENDENCIES
# RUN apk --update --upgrade add --no-cache  gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev
# RUN python -m pip install --upgrade pip

COPY . /backend
WORKDIR /backend

RUN pip install fastapi Uvicorn pydantic psycopg2-binary websockets confluent-kafka redis requests

CMD ["python", "main.py"]