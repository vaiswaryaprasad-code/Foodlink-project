
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodlink.settings")

import django
django.setup()

from django.apps import apps

models = [m for m in apps.get_models() if m._meta.app_label in ("accounts", "donor", "ngo")]

print("FOODLINK DATABASE SCHEMA")

[print("\nTABLE:", m._meta.db_table) or [print(f"{f.column} | {f.get_internal_type()} | Size: {getattr(f, 'max_length', 'N/A')} | Key: {'PK' if f.primary_key else 'FK' if f.is_relation and f.many_to_one else 'UNIQUE' if f.unique else '-'} | {f.verbose_name}") for f in m._meta.concrete_fields] for m in models]