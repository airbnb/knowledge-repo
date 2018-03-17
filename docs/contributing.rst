Contributing
============

We welcome all manner of contributions, including bug reports, feature
suggestions, documentation  improvements, and patches to support new or improved
functionality.

For developers looking to extend the Knowledge Repo, a few specific common
examples are provided below.

Adding support for new Knowledge Post conversions
-------------------------------------------------

Support for conversion of a particular filetype to a knowledge post is added by
writing a new `KnowledgePostConverter` object. Each converter should live in its
own file in `knowledge_repo/converters`. Refer to the implementation for ipynb,
Rmd, and md for more details. If your conversion is site-specific, you can
define these subclasses in `.knowledge_repo_config`, whereupon they will be
picked up by the conversion code.

Adding extra structure and/or verifications to the knowledge post conversion process
------------------------------------------------------------------------------------

When a KnowledgePost is constructed by converting from support filetypes, the
resulting post is then passed through a series of postprocessors (defined in
`knowledge_repo/postprocessors`). This allows one to modify the knowledge post,
upload images to remote storage facilities (such as S3), and/or verify some
additional structure of the knowledge posts. As above, defining or importing
these classes in `.knowledge_repo_config.py` allows for postprocessors to be
used locally.

Something else?
---------------

Please don't hesitate to file an issue on our GitHub issue tracker, and we will
get back to you when we can.
