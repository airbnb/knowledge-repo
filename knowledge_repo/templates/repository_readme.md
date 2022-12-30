# Knowledge Repository

This is a git repository that stores documents called "Knowledge Posts" in a
format compatible with that of the [Knowledge Repo](https://github.com/airbnb/knowledge-repo)
project.

If you are looking to contribute a post to this repository, please follow the
below quickstart guide or the [upstream documentation](http://knowledge-repo.readthedocs.io/en/latest/quickstart.html).

## Quickstart

1\. Install the knowledge-repo tooling
```
pip install  --upgrade "knowledge-repo[all]"
```

2\. Clone this repository to your local machine
```
git clone <git_url> <repo_path>
```
**Note:** If you regularly interact with this repository, you can avoid adding `--repo <repo_path>` in all of the below commands by exporting a shell environment variable:

```
export KNOWLEDGE_REPO="<repo_path>"
```

3\. Create a post template

For a Jupyter notebook:
```
knowledge_repo create ipynb example_post.ipynb
```

For a R markdown:
```
knowledge_repo create Rmd example_post.Rmd
```

For a general markdown:
```
knowledge_repo create md example_post.md
```

4\. Edit the notebook file `example_post.ipynb`, `example_post.Rmd`, or `example_post.md` as you normally would.

5\. Add your post to the repo with in-repository path of `project/example_post`
```
knowledge_repo add <post_file> -p project/example_post
```

6\. Preview the added post to ensure everything is rendering correctly
```
knowledge_repo preview project/example_post
```

7\. Submit post as a new git branch in this repository
```
knowledge_repo submit project/example_post
```

8\. Open a pull/merge request on your branch through GitHub

Once ready, merge your branch into master, and your post will shortly thereafter
appear in attached *Knowledge Repo* servers.