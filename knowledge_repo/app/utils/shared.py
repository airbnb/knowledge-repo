from flask import Blueprint


def get_blueprint(name, import_name):
    return Blueprint(
        name,
        import_name,
        template_folder='../templates',
        static_folder='../static')
