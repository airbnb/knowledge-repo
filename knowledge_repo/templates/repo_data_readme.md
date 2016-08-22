# The Knowledge Repository

This document is an introduction to the knowledge repository and contains instructions on how
to contribute. The Knowledge Repository hosts write-ups of research in a single, organized and accessible repository. It contains three primary types of documents:

1. Contributions to the body of knowledge your organization
2. Write-ups of projects and work in progress
3. Descriptions of methods, tips and tricks

All posts share a common format, and are automatically converted from RMarkdown, IPython, or plain text. They are stored under version control in a git repository and will be rendered as webpages the hosted knowledge repo web application.

## Initial Setup

There are two steps to getting you computer ready to contribute to the knowledge repository.
1. Install the `knowledge_repo` package and script.
2. Check out this repository to your machine.


### Installing `knowledge_repo`
To prepare your computer with the software required to contribute to the repository, you must install the open source python library `knowledge_repo`. Doing this is as simple as:

`pip install git+ssh://git@github.com/airbnb/knowledge-repo.git`

This installs the python library as well as the `knowledge_repo` script that you will be using to interact with the knowledge repository.

### Checking out the `knowledge` repository
With that done, all that remains for you to do is to checkout this repository to a folder on your computer. 

If you set the `KNOWLEDGE_REPO` environment variable in your `.bash_profile` file, you will not need to specify the `--repo` argument to the `knowledge_repo` script as shown below. You can do this by adding the following:

`export KNOWLEDGE_REPO=/path/to/this/repo`

## TLDR Guide For Contributing

If you have already set up your system as described below, here is a snapshot of the commands you need to run to upload your knowledge post stored in ~/Documents/my_post.ipynb. It assumes you have configured the KNOWLEDGE_REPO environment variable to point to your local copy of the knowledge repository.

1. knowledge_repo create ipynb ~/Documents/my_post.ipynb
2. knowledge_repo add ~/Documents/my_post.ipynb [-p projects/test_project] [--update]
3. knowledge_repo preview projects/test_project
4. knowledge_repo submit projects/test_project
5. [If applicable] Open a PR in GitHub or other git web UI
6. After it has been reviewed, merge it in to master.

For more details, read on.

### Creating a new post

Now the fun bit! Writing new posts. Go crazy! Anything is allowed. The web interface to the repo will render your posts for you, automatically converting from the following formats:

* IPython Notebook (ipynb)
* RMarkdown (Rmd)
* Simple Markdown (md)

So long as the post you create is in one of these formats, and satisfies the constraints described below, you're good to go.

The easiest workflow is to do your research and write straight into one of these formats, so that when the time comes to actually contribute it, you don't have much overhead in transcribing your work.

The internal knowledge post format is based on markdown, so you can use the vast majority of its features in your posts. If you are unfamiliar with Markdown syntax, you can read up about it online at a number of sites.

### Constraints

The knowledge repository does a pretty good job of converting posts from their original formats into its internal representation. However, it requires certain structural features; and there are other considerations to increase the uniformity of posts throughout the knowledge repository.

#### Required Constraints

__!!! Do not create and edit your posts within the checked out knowledge repository itself. If you do, you run the risk of losing work !!!__

All posts must have a YAML header such as the one below:
```
---
title: This is a Knowledge Template Header
authors:
- sally_smarts
- wesley_wisdom
tags:
- knowledge
- example
created_at: 2016-08-18
updated_at: 2016-08-19
tldr: This is short description of the content and findings of the post.
---
```
Failure to have such a header will result in the post not being submitted to the knowledge repository. You can either copy and paste this at the top of your existing file (make sure the cell is a markdown or raw cell in Jupyter notebooks), or we recommend getting started with a template that already contains a sample header. To do this, use the following command.

`knowledge_repo --repo <knowledge_repo_path> create <format> <path where template should be created>`

For example:

`knowledge_repo --repo /path/to/local/repo create ipynb ~/Documents/test.ipynb`

NOTE: If you want more complex formatting in your `tldr` you can write arbitrary markdown given you escape the field like so: 

```
tldr: |
    You can write any markdown you want here (this is an escaped section)

    * bullet 1
    * bullet 2

    You can even write arbitrary html (html is valid markdown)
    <table>
    <tr>
    <th>I'm</th>
    <th>a table</th>
    </tr>
    </table>

```

It may be useful to interactively create your yaml header at a site like http://yaml-online-parser.appspot.com/ in order to quickly see that it's valid.

#### Consistency Constraints

* After your headers, include a table of contents section. This both gives a preview of the topics you will be discussing, and also allows you to send links to specific sections of your post. You can create a table of contents by adding this to your source code:

```
**Table of Contents**

[TOC]
```

* Try to use tags that already exist, rather than creating your own. 

## Submitting your post to the repository

Once you are happy with your post, it's time to submit it to the repository. This is mostly taken care of (again) by the `knowledge_repo` script.

### 1. Add your post to your local repository

In simplest (and most common) scenario, where all of your work is done in a single file, adding to the repository will look something like this:

`knowledge_repo --repo <knowledge_repo_path> add <source_filename> <project_path> --push`

This will convert your post (see appendix for more format-specific options), add and commit your post to a folder in the knowledge repository at `<project_path>` on a git branch by the same name (or with '.kp' appended). It will create this branch if it does not exist, or append commits if it does. 

Other useful options include `--src <file1> <folder1> <file2>...` which adds source files to your project. Note that you do not need to specify your original post as a source file; since it is added automatically as such. You can push this post upstream for review (in its branch) directly as is, if you are super confident, using the `--push` option.

For a complete run down of options, look at:

`knowledge_repo --repo <knowledge_repo_path> add --help`

### 2. Preview your post locally

While the knowledge repo does a good job converting your posts, there are always going to be small formatting differences between your local viewers and what gets rendered on the server. It is a good idea to check how it is going to render on the server using:

`knowledge_repo --repo <knowledge_repo_path> preview <project_path>`

This will spin up your own copy of the knowledge repository website, and load up your post in your browser.

Note that this assumes that you are still checked out on your projects branch. If you have added or looked at others' posts, you need to check out your projects branch again using:

`knowledge_repo --repo <knowledge_repo_path> checkout <project_branch>`

or manually using git. You can see which branch you are currently on using:

`knowledge_repo --repo <knowledge_repo_path> status`

### 3. Push your changes upstream

If you've been cautious and didn't shortcut the previewing process, and your post looks good, you can now push it upstream for review. You can do this manually in git or by using:

`knowledge_repo --repo <knowledge_repo_path> push <project_branch>`

### 4. [If applicable] Open a pull request in Github or other git web ui

Visit this repo's git web ui and create a new pull request. In GitHub this is done from the yellow bar that appears above the files currently in the repo. The branch to be merged should have the same name as the path of your post.

Be sure to **label your pull request** with the appropriate label. For example, your organization might use:

* **WIP** - _"this is a work in progress, don't look yet"_
* **Review** - _"this is ready to be reviewed"_ - Someone in your organization should take a look as soon as possible, hopefully within a day or so.
* **Urgent** - _"I need to sent this out asap, please ok it"_ - In case the review needs to get done quickly.

### 4. Have your post reviewed

To make sure your research is high quality, it is good to get it reviewed by peers. In general it's good practice to add anyone who might know something about your topic or might be interested to make them aware of your work. It is a good idea to create a pull request early on, so you get feedback early in the writing process!

The repository is set-up so that reviewers can comment directly on text files, but also render them in semi-completed format with Github's 'View' mode for the 'knowledge.md' files. Feedback and comments can be left either in-line or in the 'Conversation' section of the Github UI.


### 5. Integrate the reviewers' comments and merge!

Once you have received comments from your peers, integrated them and received an approval, you can merge your branch into master. Once the PR is merged it will appear on the knowledge repo website in the space of a few minutes. Remember that the `/feed` view sorts by date, so remember to correctly set the `updated-at` date in your post header; otherwise your post might appear lower down the list than it should.

## Appendix

#### R Markdown

If you'd like to use R Markdown, you can set it up using the process below:

1. Download, install and open RStudio
2. Install R packages by running `install.packages`. For example, to install the R markdown package, execute `install.packages("rmarkdown")`.
3. Copy the RMarkdown template
`knowledge_repo --repo <repository_path> create Rmd <path>.Rmd`.
4. When you're ready to build the file, use the knit button (shift+command+k).

#### IPython/Jupyter Notebook

If you'd like to use a IPython Notebook, you can set it up using the process below:

1. The easiest way to install all the required packages is to install [Anaconda](http://continuum.io/downloads).
2. Alternatively, run `pip install "jupyter[notebook]"`
3. Start IPython with `jupyter notebook`.
4. Copy the IPython template
`knowledge_repo --repo <repository_path> create ipynb <path>.ipynb`.

### Knowledge Repository Web UI Tips

* You can Subscribe to tags when hovering over them (after which you will receive emails for new posts with that tag).
* You can like posts by clicking the heart icon. The posts you liked will be collected under the favorites tab.

