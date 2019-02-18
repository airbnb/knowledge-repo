DBPATH=$KR_REPO_DB_URI
USER=$KR_REPO_DB_USER
PSWD=$KR_REPO_DB_PWD
PORT=$KR_REPO_DB_PORT
SQLCONN="mysql://$USER:$PSWD@$DBPATH:$PORT/knowledgerepo"

#source /app/kr/bin/activate

CMD="/app/scripts/knowledge_repo --repo {webpost}$SQLCONN:webposts --repo {webpost2}$SQLCONN:webposts2 runserver --config=/app/app_config.py --port 80"
echo $CMD
$($CMD)
