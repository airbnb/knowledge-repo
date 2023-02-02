from flask import current_app
from flask_login import current_user
from werkzeug.local import LocalProxy
from knowledge_repo.utils.s3 import get_s3_client
from knowledge_repo.utils.notion import get_notion_client

__all__ = ["db_session", "current_repo", "current_user"]

db_session = LocalProxy(lambda: current_app.db.session)
current_repo = LocalProxy(lambda: current_app.repository)
s3_client = LocalProxy(
    lambda: get_s3_client(
        current_app.config.get("S3_AWS_ACCESS_KEY_ID", ""),
        current_app.config.get("S3_AWS_SECRET_ACCESS_KEY", ""),
        current_app.config.get("S3_AWS_REGION_NAME", "us-west-2"),
    )
)
notion_client = LocalProxy(
    lambda: get_notion_client(current_app.config.get("NOTION_AUTH", ""))
)
