
# This is a stub to be replaced with more sophisticated system tests

sleep 5
# check that GET /feed serves something
if curl web/feed | grep -q 'Served with <span class="glyphicon glyphicon-heart"></span> by <a href="https://github.com/airbnb/knowledge-repo">Knowledge Repo</a>'; then
  echo "Tests passed!"
  exit 0
else
  echo "Tests failed!"
  exit 1
fi
