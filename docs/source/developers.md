

## Contributing

We would love to work with you to create the best knowledge repository software possible. If you have ideas or would like to have your own code included, add an issue or pull request and we will review it.

### Adding new filetype support

Support for conversion of a particular filetype to a knowledge post is added by writing a new `KnowledgePostConverter` object. Each converter should live in its own file in `knowledge_repo/converters`. Refer to the implementation for ipynb, Rmd, and md for more details. If your conversion is site-specific, you can define these subclasses in `.knowledge_repo_config`, whereupon they will be picked up by the conversion code.

### Adding extra structure and/or verifications to the knowledge post conversion process

When a KnowledgePost is constructed by converting from support filetypes, the resulting post is then passed through a series of postprocessors (defined in `knowledge_repo/postprocessors`). This allows one to modify the knowledge post, upload images to remote storage facilities (such as S3), and/or verify some additional structure of the knowledge posts. As above, defining or importing these classes in `.knowledge_repo_config.py` allows for postprocessors to be used locally.

### More

Is the Knowledge Repository missing something else that you would like to see? Let us know, and we'll see if we cannot help you.
