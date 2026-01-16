import os
import django
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

def get_model_signature(model):
    columns = []
    for field in model._meta.get_fields():
        if field.concrete and not field.many_to_many:
            if field.is_relation and field.many_to_one:
                 columns.append(field.attname) # usually field_id
            else:
                 columns.append(field.column)
    return sorted(columns)

print("--- MODEL SIGNATURES ---")
for model in apps.get_models():
    sig = get_model_signature(model)
    print(f"Model: {model._meta.label}, Signature: {','.join(sig)}")

    # Check for M2M fields and their through models
    for field in model._meta.many_to_many:
        if field.remote_field.through and field.remote_field.through._meta.auto_created:
             through_model = field.remote_field.through
             t_sig = get_model_signature(through_model)
             print(f"Model (Through): {through_model._meta.label}, Signature: {','.join(t_sig)}")
