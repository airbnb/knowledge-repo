## Server Configuration

Running the web app allows you to locally view all the knowledge posts in the repository, or to serve it for others to view. It is also useful when developing on the web app.

### Running the development server

Running the web app in development/local/private mode is as simple as running:

`knowledge_repo --repo <repo_path> runserver`

Supported options are `--port` and `--dburi` which respectively change the local port on which the server is running, and the sqlalchemy uri where the database can be found and/or initiated. The default port is 7000, and the default dburi is `sqlite:////tmp/knowledge.db`. If the database does not exist, it is created (if that is possible) and initialised. Database migrations are automatic (unless disabled to prevent accidental data loss), but can be performed manually using:

`knowledge_repo --repo <repo_path> db_upgrade --dburi <db>`

### Running the Web App on Multiple Repos

The web application can be run on top of multiple knowledge repo backends. To do this, include each repo with a name and path, prefixed by --repo. For example:

`knowledge_repo --repo {git}/path/to/git/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable runserver`

If including a dbrepo, add the name of the dbrepo to the `WEB_EDITOR_PREFIXES` in the server config, and add it as config when running the app:

`knowledge_repo --repo {git}/path/to/git/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable runserver --config resources/server_config.py`

Note that this is required for the web application's internal post writing UI.

### Deploying the web app

Deploying the web app is much like running the development server, except that the web app is deployed on top of gunicorn. It also allows for enabling server-side components such as sending emails to subscribed users.

Deploying is as simple as:
`knowledge_repo --repo <repo_path> deploy`

or if using multiple repos:
`knowledge_repo --repo {git}/path/to/git/repo --repo {webposts}sqlite:////tmp/dbrepo.db:mypostreftable deploy --config resources/server_config.py`

Supported options are `--port`, `--dburi`,`--workers`, `--timeout` and `--config`. The `--config` option allows you to specify a python config file from which to load the extended configuration. A template config file is provided in `resources/server_config.py`. The `--port` and `--dburi` options are as before, with the `--workers` and `--timeout` options specifying the number of threads to use when serving through gunicorn, and the timeout after which the threads are presumed to have died, and will be restarted.
