`python-editor` is a library that provides the `editor` module for programmatically
interfacing with your system's $EDITOR.

Examples
--------

```python
import editor
commit_msg = editor.edit(contents=b"# Enter commit message here")
```

Opens an editor, prefilled with the contents, `# Enter commit message here`.
When the editor is closed, returns the contents (bytes) in variable `commit_msg`.
Note that the argument to `contents` needs to be a bytes object on Python 3.


```python
editor.edit(file="README.txt")
```

Opens README.txt in an editor.  Changes are saved in place.  If there is
a `contents` argument then the file contents will be overwritten.

```python
editor.edit(..., use_tty=True)
```

Opens the editor in a TTY.  This is usually done in programs which output is
piped to other programs.  In this case the TTY is used as the editor's stdout,
allowing interactive usage.


How it Works
------------

`editor` first looks for the ${EDITOR} environment variable.  If set, it uses
the value as-is, without fallbacks.

If no $EDITOR is set, editor will search through a list of known editors, and
use the first one that exists on the system.

For example, on Linux, `editor` will look for the following editors in order:

* vim
* emacs
* nano

When calling `editor.edit`, an editor will be opened in a subprocess, inheriting
the parent process's stdin, stdout.


