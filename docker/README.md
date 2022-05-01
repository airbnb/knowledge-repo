# Docker

Make sure you have Docker installed, and Docker Desktop is running.

## Build an image

In the knowledge-repo folder, run the following command:

<pre>
docker build -t knowledge -f docker/Dockerfile .
</pre>

## Run it locally

<pre>
docker run --rm -it -p 7000:7000 -e KNOWLEDGE_REPO=test_repo knowledge
</pre>

After the server is up and running in Docker, the knowledge-repo service will be accessible at http://localhost:7000. If the 7000 port number is being used by another process, you may choose another local port number to use, e.g., the following command starts the service at port number 7001 (i.e., http://localhost:7001):

<pre>
docker run --rm -it -p 7001:7000 -e KNOWLEDGE_REPO=test_repo knowledge
</pre>

## Run it locally with a mapped notebook-folder

<pre>
docker run --rm -it -p 7000:7000 -v &lt;notebook-folder&gt;:/data -e KNOWLEDGE_REPO=test_repo knowledge
</pre>
