# Docker

Make sure you have Docker installed

## Build an image

<pre>
docker build -t knowledge -f docker/Dockerfile.dev .
</pre>

## Run it locally

<pre>
docker run --rm -it -p 7000:7000 -v &lt;notebook-folder&gt;:/data -e KNOWLEDGE_REPO=test_repo knowledge
</pre>
