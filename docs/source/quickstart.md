
# Quickstart

## 1\. Install the knowledge-repo tooling
```
pip install  --upgrade knowledge-repo
```

To install dependencies for iPython notebook, PDF uploading, and local development, use `pip install --upgrade knowledge-repo[all]`

## 2\. Initialize a knowledge repository - your posts will get added here
```
knowledge_repo --repo ./example_repo init
```

## 3\. Create a post template

for Rmd:
```
knowledge_repo --repo ./example_repo create Rmd example_post.Rmd
```

for ipynb
```
knowledge_repo --repo ./example_repo create ipynb example_post.ipynb
```

## 4\. Edit the notebook file `example_post.ipynb` or `example_post.Rmd` as you normally would.


## 5\. Add your post to the repo with path `project/example`
```
knowledge_repo --repo ./example_repo add example_post.Rmd -p project/example_rmd
knowledge_repo --repo ./example_repo add example_post.ipynb -p project/example_ipynb
```

## 6\. Preview the added post
```
knowledge_repo --repo ./example_repo preview project/example_rmd
#or
knowledge_repo --repo ./example_repo preview project/example_ipynb
```
