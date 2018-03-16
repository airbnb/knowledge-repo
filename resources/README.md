Resources
=========

This folder contains useful resources for setting up a knowledge repository.

In particular, you will find:
 - extract_images_to_s3.py : An example of a custom postprocessor that you can
   include in your local knowledge repository configuration (by simply importing
   it), that uploads images to an S3 server instead of adding them to the
   knowledge data repository.
 - extract_images_to_local.py : An example of a custom postprocessor that you
   can include in your local knowledge repository configuration (by simply
   importing it), that copies images to a local directory instead of adding them
   to the `post-name.kp` directory. A simple http-server through python or npm can then be used to serve images from that local directory

For a template server configuration file, please refer to
['../knowledge_repo/app/config_defaults.py'](https://github.com/airbnb/knowledge-repo/blob/master/knowledge_repo/app/config_defaults.py). You can then use this
configuration to deploy a server instance using:

     $ knowledge_repo --repo <repo> deploy --config <filename>
