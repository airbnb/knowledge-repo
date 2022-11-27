FROM python:3.9

LABEL description="knowledge-repo V2 service "

# Define some build time variables
ARG PIP=pip3

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y netcat

# Setup Expose port
EXPOSE 5050

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN ${PIP} install -r requirements.txt

# Copy project
COPY . ./

# Run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "app.py"]
