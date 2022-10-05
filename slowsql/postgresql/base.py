from django.db.backends.postgresql import base


class DatabaseWrapper(base.DatabaseWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.force_debug_cursor = True
