
# Overview

Knowledge posts are a general markdown format that is automatically generated from the following common formats:

 - Jupyter/Ipython notebooks
 - Rmd notebooks
 - Markdown files

The Jupyter, Rmd, and Markdown files are required to have a specific set of yaml style headers which are used to organize and discover research:

```
---
title: I Found that Lemurs Do Funny Dances
authors:
- sally_smarts
- wesley_wisdom
tags:
- knowledge
- example
created_at: 2016-06-29
updated_at: 2016-06-30
tldr: This is short description of the content and findings of the post.
---
```

*See a full description of headers [further below](https://github.com/airbnb/knowledge-repo#post-headers)*

Users add these notebooks/files to the knowledge repository through the `knowledge_repo` tool, as described below; which allows them to be rendered and curated in the knowledge repository's web app.

If your favourite format is missing, we welcome contributions; and are happy to work with you to get it supported. See the "Contributing" section below to see how to add support for more formats.

Note that the web application can live on top of multiple Knowledge Repo backends. Supported types so far are:

 - Git Repo + Remote Git Hosting Service (Primary Use Case)
 - Web Application SQL db

## Getting started
There are two repositories associated with the Knowledge Repository project.
1. This repository, which will be installed first. This is referred to as the knowledge repository tooling.
2. A knowledge data repository, which is created second. This is where the knowledge posts are stored.
