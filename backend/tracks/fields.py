import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class JSONField(models.TextField):
    """
    A JSONField that uses the json module to serialize/deserialize data.
    """
    def to_python(self, value):
        if not value: 
            return None
        return json.loads(value)

    def from_db_value(self, value, *args):
        return self.to_python(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        value_for_db = None
        if isinstance(value, dict):
            value_for_db = json.dumps(value, cls=DjangoJSONEncoder)
        return value_for_db
