# Knowledge Repository

This is a git repository that stores documents called "Knowledge Posts" in a
format compatible with the [Knowledge Repo](https://github.com/airbnb/knowledge-repo)
project.

If you are looking to contribute a post to this repository, please refer to the
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
**Note:** If you regularly interact with this repository, you can avoid having to type `--repo <repo_path>` in all of the below commands by exporting a shell environment variable:

```
export KNOWLEDGE_REPO="<repo_path>"
```

3\. Create a post template

For Jupyter notebooks:
```
knowledge_repo --repo <repo_path> create ipynb example_post.ipynb
```

For R Markdown:
```
knowledge_repo --repo <repo_path> create Rmd example_post.Rmd
```

4\. Edit the notebook file `example_post.ipynb` or `example_post.Rmd` as you normally would.

5\. Add your post to the repo with in-repository path of `project/example`
```
knowledge_repo --repo <repo_path> add <post_path> -p project/example
```

6\. Preview the added post to ensure everything is rendering correctly
```
knowledge_repo --repo <repo_path> preview project/example
```

7\. Submit post as a new git branch in this repository
```
knowledge_repo --repo <repo_path> submit project/example
```

8\. Open a pull/merge request on your branch

Once ready, merge your branch into master, and your post will shortly thereafter
appear in attached *Knowledge Repo* servers.
