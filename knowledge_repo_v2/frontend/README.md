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

After running in Docker, the knowledge-repo frontend will be accessible at http://localhost:3000.
