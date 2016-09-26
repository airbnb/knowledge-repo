import os
from setuptools import setup, find_packages
from distutils import log
from distutils.command.install_scripts import install_scripts

# Extract version info from library
version_info = {}
with open('knowledge_repo/_version.py') as version_file:
    exec(version_file.read(), version_info)

# Batch file template for Windows (based on https://github.com/matthew-brett/myscripter/blob/master/setup.py)
BATCHFILE_TEMPLATE = r"""
@echo off
REM Wrapper around {script_name} to execute script in Windows using the interpreter specified with the hashbang
set dirname=%~dp0
set wrapped_script="%dirname%{script_name}"
set /p line1=<%wrapped_script%
if "%line1:~0,2%" == "#!" (goto :execute)
echo First line of %wrapped_script% does not start with "#!"
exit /b 1
:execute
set py_exe=%line1:~2%
call "%py_exe%" %wrapped_script% %*
"""


# Custom script installer for Windows (based on https://github.com/matthew-brett/myscripter/blob/master/setup.py)
class install_scripts_windows_wrapper(install_scripts):
    def run(self):
        install_scripts.run(self)
        if not os.name == "nt":
            return
        for script_path in self.get_outputs():
            # If we can find an executable name in the #! top line of the script
            # file, make .bat wrapper for script.
            with open(script_path) as fobj:
                first_line = fobj.readline()
            if not (first_line.startswith('#!') and 'python' in first_line.lower()):
                log.info("Script does not appear to be a python executable. Skipping creation of batchfile wrapper")
                continue
            script_dirname, script_basename = os.path.split(script_path)
            script_name, _ = os.path.splitext(script_basename)
            batchfile_path = os.path.join(script_dirname, script_name + '.bat')
            log.info("Making batchfile wrapper at {} (for {})".format(batchfile_path, script_path))

            batchfile_content = BATCHFILE_TEMPLATE.format(script_name=script_name)

            if self.dry_run:
                continue
            with open(batchfile_path, 'w') as fobj:
                fobj.write(batchfile_content)


setup(
    name='knowledge_repo',
    description=(
        " A workflow for contributing company knowledge, in the form "
        " of RMarkdowns, iPythons, and Markdowns, rendered and organized"
        " to magnify research impact across teams and time "),
    version=version_info['__version__'].split('_')[0],  # remove git revision if present
    author=version_info['__author__'],
    author_email=version_info['__author_email__'],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,  # See included paths in MANIFEST.in
    scripts=['scripts/knowledge_repo'],
    install_requires=version_info['__dependencies__'],
    extras_require=version_info['__optional_dependencies__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    cmdclass={'install_scripts': install_scripts_windows_wrapper}
)
