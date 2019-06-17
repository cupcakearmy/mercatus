# BUILDER
FROM python:3.7-alpine as builder
RUN apk add --no-cache alpine-sdk libffi-dev openssl-dev python3-dev freetype-dev
COPY requirements.txt .
RUN pip install -r requirements.txt

# APP
FROM python:3.7-alpine
RUN apk add --no-cache libstdc++ freetype
WORKDIR /app

COPY --from=builder /root/.cache /root/.cache
COPY --from=builder requirements.txt .
RUN pip install -r requirements.txt && rm -rf /root/.cache

#COPY src .
#CMD ["python", "-u", "/app/Mercatus.py"]