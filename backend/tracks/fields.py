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
        # ---- Checks if the Django encoder was used to serialize the data.
        # If the value is a single-quote string, replace it with a double-quote string.
        if isinstance(value, str) and "'" in value:
            value = value.replace("'", '"')
        # When the string contains symbols like Ã\\x9f (ß), we need to use the correct encoding.
        if isinstance(value, str) and "\\x" in value:
            value = bytes(value, "utf-8").decode("unicode_escape")
        # Convert uppercase True and False to lowercase, and None to null.
        if isinstance(value, str):
            value = value.replace("True", "true").replace("False", "false")
            value = value.replace("None", "null")
        # ---- End of checks
        try:
            return json.loads(value)
        except (TypeError, ValueError) as e:
            # Print out a detailed error message.
            print(f"Error: {e}")
            print(value)
            raise

    def from_db_value(self, value, *args):
        return self.to_python(value)

    def get_db_prep_save(self, value, *args, **kwargs):
        value_for_db = None
        if isinstance(value, dict):
            value_for_db = json.dumps(value, cls=DjangoJSONEncoder)
        return value_for_db
