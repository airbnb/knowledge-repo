from notion_client import Client, AsyncClient
import logging
from notion_client import APIResponseError
from knowledge_repo.constants import KP_EDIT_PROD_LINK

logger = logging.getLogger(__name__)


def get_notion_client(auth):
    """Get a notion synchronous client for notion synchronous operations

    :param auth: Bearer token for authentication
    :return: a notion client for notion sync operations
    """
    return Client(auth=auth)


def get_notion_async_client(auth):
    """Get a notion asynchronous client for notion asynchronous operations

    :param auth: Bearer token for authentication
    :return: a notion async client for notion async operations
    """
    return AsyncClient(auth=auth)


def query_page(notion_client, page_id):
    """Retrieve a Page object using the page ID specified

    :param notion_client: a notion client
    :param pag_id: Identifier for a Notion page
    :return: page object if found, else False
    """
    try:
        logger.info(notion_client.pages.retrieve(page_id))
    except APIResponseError as error:
        logging.error(error)
    return False


def create_page(notion_client, database_id, params):
    """Create a new page in the specified database

    :param notion_client: a notion client
    :param params: property values of this page.
    :return: True if page was created, else False
    """

    name = params.get("title", None)
    description = params.get("tldr", "")
    tags = [{"name": t} for t in params.get("tags", [])]
    path = params.get("path", "")
    if len(path) > 0:
        post_link = "/".join([KP_EDIT_PROD_LINK, path])
        logger.info(post_link)
    else:
        post_link = ""
    file_link = params.get("display_link", "")

    if name is None:
        logger.error("Page Name is Empty")
        return False

    try:
        notion_client.pages.create(
            parent={
                "type": "database_id",
                "database_id": database_id,
            },
            properties={
                "Name": {"title": [{"text": {"content": name}}]},
                "Description": {"rich_text": [{"text": {"content": description}}]},
                "Tags": {"multi_select": tags},
                "Knowledge Repo Link": {
                    "rich_text": [
                        {"text": {"content": post_link, "link": {"url": post_link}}},
                    ]
                },
                "Original File Link": {"rich_text": [{"text": {"content": file_link}}]},
            },
        )
    except APIResponseError as error:
        logging.error(error)
        return False
    return True
