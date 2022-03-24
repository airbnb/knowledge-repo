import pkg_resources


def check_dependencies(dependencies, message=None):
    missing_deps = []
    for dep in dependencies:
        try:
            pkg_resources.get_distribution(dep)
        except Exception as e:
            print(f'Exception encountered: {e}')
            missing_deps.append(dep)
    if missing_deps:
        message = message or \
            'Whoops! You do not seem to have all the dependencies required.'
        install_command = 'pip install --upgrade ' + ' '.join(missing_deps)
        fix = ("You can fix this by running:\n\n"
               f"\t{install_command}\n\n"
               "Note: Depending on your system's installation of Python, "
               "you may need to use `pip2` or `pip3` instead of `pip`.")
        raise RuntimeError(f'{message}\n\n{fix}')
