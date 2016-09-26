import pkg_resources


def check_dependencies(dependencies, message=None):
    missing_deps = []
    for dep in dependencies:
        try:
            pkg_resources.get_distribution(dep)
        except:
            missing_deps.append(dep)
    if missing_deps:
        message = message or "Whoops! You do not seem to have all the dependencies required."
        fix = ("You can fix this by running:\n\n"
               "\t{install_command}\n\n"
               "Note: Depending on your system's installation of Python, you may "
               "need to use `pip2` or `pip3` instead of `pip`.").format(install_command='pip install --upgrade ' + ' '.join(missing_deps))
        raise RuntimeError('\n\n'.join([message, fix]))
