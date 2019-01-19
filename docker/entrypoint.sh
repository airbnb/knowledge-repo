#!/bin/bash

scripts/knowledge_repo init

for ext in 'md' 'docx' 'zip' 'gdoc' 'html' 'kp' 'ipynb' 'rmd' 'proxy'
do
  find /data -name "*.$ext" -not -path '*.ipynb_checkpoints/*' | xargs -I{} sh -c 'base=$(basename "{}"); scripts/knowledge_repo add "{}" -p "$base"'
done

scripts/knowledge_repo runserver
