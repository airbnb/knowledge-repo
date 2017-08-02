from functools import partial
from flask_principal import RoleNeed, ItemNeed

# Need types
GroupNeed = partial(ItemNeed, 'group')

# Site roles
admin = RoleNeed('admin')
stats_view = RoleNeed('stats_view')

# Index roles
index_view = RoleNeed('index_view')

# Post roles
post_comment = RoleNeed('post_comment')
post_edit = RoleNeed('post_edit')
post_view = RoleNeed('post_view')
post_download = RoleNeed('post_download')
