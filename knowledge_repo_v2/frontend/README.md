# Docker

Make sure you have Docker installed, and Docker Desktop is running.

## Build an image

In the knowledge-repo/knoweledge_repo_v2/frontend folder, run the following command:

<pre>
docker build . -t kp2-frontend
</pre>

## Run it locally

<pre>
docker run -p 3000:3000 kp2-frontend
</pre>

After the server is up and running in Docker, the knowledge-repo service will be accessible at http://localhost:5050.
