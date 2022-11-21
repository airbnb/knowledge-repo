FROM python:3.9

LABEL description="knowledge-repo V2 service "

# Define some build time variables
ARG PIP=pip3

WORKDIR /app

EXPOSE 5050

COPY requirements.txt ./

RUN ${PIP} install -r requirements.txt

COPY . ./

CMD ["python", "app.py"]
