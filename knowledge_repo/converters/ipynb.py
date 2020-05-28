import os

from ..converter import KnowledgePostConverter
from .._version import __optional_dependencies__

TEMPLATE = '''
{%- extends 'markdown.tpl' -%}

{%- block data_javascript scoped %}
{% set div_id = uuid4() %}
<div id="{{ div_id }}"></div>
<div class="output_subarea output_javascript {{ extra_class }}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
{{ output.data['application/javascript'] }}
</script>
</div>
{%- endblock -%}

{%- block input -%}
{%- if cell['metadata'].get('slideshow',{}).get('slide_type','') == 'skip' -%}
{%- else %}
```python
{{ cell.source }}
```
{%- endif %}
{%- endblock input -%}

{%- block data_priority scoped %}
{{ super() }}
{%- endblock %}


{# remove stderr output #}
{%- block stream scoped -%}
    {%- if output.name == 'stdout' -%}
        {{ super () }}
    {%- elif output.name == 'stderr' -%}
    {%- endif -%}
{%- endblock stream -%}
'''


class IpynbFormat(KnowledgePostConverter):
    _registry_keys = ['ipynb']

    @property
    def dependencies(self):
        return __optional_dependencies__['ipynb']

    def from_file(self, filename):
        import nbformat
        from nbconvert import MarkdownExporter
        from jinja2 import DictLoader
        from traitlets.config import Config

        c = Config()
        # c.ExtractOutputPreprocessor.extract_output_types = set()
        c.ExtractOutputPreprocessor.output_filename_template = 'images/{unique_key}_{cell_index}_{index}{extension}'
        c.NbConvertBase.display_data_priority = ['application/javascript', 'text/html', 'text/markdown',
                                                 'image/svg+xml', 'text/latex', 'image/png', 'image/jpeg',
                                                 'text/plain']

        nb = nbformat.read(filename, as_version=4)

        dl = DictLoader({'full.tpl': TEMPLATE})
        md_exporter = MarkdownExporter(config=c, extra_loaders=[
                                       dl], template_file='full.tpl')
        (body, resources) = md_exporter.from_notebook_node(nb)

        self.kp_write(body, images={name.split(
            'images/')[1]: data for name, data in resources.get('outputs', {}).items()})

        # Add cleaned ipynb file
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell['outputs'] = []  # remove output data
                cell['execution_count'] = None  # reset to not executed
        self.kp.write_src(os.path.basename(filename), nbformat.writes(nb))
