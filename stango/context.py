def dict_merge(*args):
    result = {}
    for d in args:
        result.update(d)
    return result

class Context(object):
    def __init__(self, manager, filespec):
        self.manager = manager
        self.path = filespec.path
        self.realpath = filespec.realpath(manager.index_file)
        self.jinja_env = None

        # One of these is set to True by the manager
        self.generating = False
        self.serving = False

    def render_template(self, template_name, **kwargs):
        builtin_template_args = {
            'generating': self.generating,
            'serving': self.serving,
            'path': self.path,
            'realpath': self.realpath,
        }

        if not self.jinja_env:
            try:
                self.jinja_env = self.manager._jinja_env
            except AttributeError:
                # Create the Jinja environment once and save it to the
                # manager instance
                from jinja2 import Environment, FileSystemLoader
                loader = FileSystemLoader(self.manager.template_dirs)
                env = Environment(loader=loader)
                self.jinja_env = self.manager._jinja_env = env

        template = self.jinja_env.get_template(template_name)
        return template.render(dict_merge(builtin_template_args, kwargs))
