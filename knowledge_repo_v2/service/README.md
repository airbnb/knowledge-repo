# Docker

Make sure you have Docker installed, and Docker Desktop is running.

## Build an image

In the knowledge-repo folder, run the following command:

<pre>
docker build . -t kp2-server
</pre>

## Run it locally

<pre>
docker run -p 5050:5050 kp2-server
</pre>

After the server is up and running in Docker, the knowledge-repo service will be accessible at http://localhost:5050.
