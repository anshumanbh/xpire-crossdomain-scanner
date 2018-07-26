FROM python:2.7.15-alpine3.8
RUN apk add gcc build-base libxslt-dev jpeg-dev zlib-dev

ADD crossdomain-scan.py crossdomain.py requirements.txt /root/crossdomain/

WORKDIR /root/crossdomain
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "crossdomain-scan.py" ]
