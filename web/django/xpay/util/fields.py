from django.db import models

class ForeignKeyAcrossDB(models.IntegerField):
    def __init__(self, model_on_other_db, **kwargs):
        self.model_on_other_db = model_on_other_db
        super(ForeignKeyAcrossDB, self).__init__(**kwargs)

    def to_python(self, value):
        if isinstance(value, self.model_on_other_db):
            return value
        else:
            return self.model_on_other_db._default_manager.get(pk=value)

    def get_prep_value(self, value):
        if isinstance(value, self.model_on_other_db):
            return value.pk
        return super(ForeignKeyAcrossDB, self).get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        return super(ForeignKeyAcrossDB, self).get_prep_lookup(lookup_type,value)
