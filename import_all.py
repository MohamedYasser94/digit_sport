import os
import csv
import sys
import django
import time

# Remove the stdout redirection for now to avoid complexity if it's causing issues
# log_file = open('script_run.log', 'w', encoding='utf-8')
# sys.stdout = log_file
# sys.stderr = log_file
debug_file = open('import_debug.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg) # still print to stdout
    debug_file.write(str(msg) + "\n")
    debug_file.flush()

log("Script started.")

# Setup Django first!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from django.db import transaction
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

def get_signature_map():
    sig_map = {}
    for model in apps.get_models():
        columns = []
        for field in model._meta.get_fields():
            if field.concrete and not field.many_to_many:
                if field.is_relation and field.many_to_one:
                     columns.append(field.attname)
                else:
                     columns.append(field.column)
        sig = frozenset(columns)
        sig_map[sig] = model

        # Check for M2M fields and their through models
        for field in model._meta.many_to_many:
            if field.remote_field.through and field.remote_field.through._meta.auto_created:
                through_model = field.remote_field.through
                t_columns = []
                for t_field in through_model._meta.get_fields():
                    if t_field.concrete and not t_field.many_to_many:
                        if t_field.is_relation and t_field.many_to_one:
                            t_columns.append(t_field.attname)
                        else:
                            t_columns.append(t_field.column)
                t_sig = frozenset(t_columns)
                sig_map[t_sig] = through_model
    return sig_map

def scan_mappings(csv_path):
    # Maps to build
    source_ct_map = {} # old_ct_id -> new_ct_id
    permission_id_map = {} # old_perm_id -> new_perm_id

    # Pre-fetch Target ID lookups
    target_model_map = {} # model_name -> list of CT IDs
    for ct in ContentType.objects.all():
        target_model_map.setdefault(ct.model, []).append(ct.id)

    # Pre-fetch Perm lookups
    # (codename, ct_id) -> perm_id
    target_perm_map = {}
    for p in Permission.objects.all():
        target_perm_map[(p.codename, p.content_type_id)] = p.id

    log("Scanning CSV for ID mappings (CT and Permissions)...")

    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)

        # State machine
        in_permission_table = False
        perm_header = None

        for row in reader:
            if not row: continue

            # Detect Permission Table Header
            if 'codename' in row and 'content_type_id' in row and 'name' in row and 'id' in row:
                if len(row) <= 5: # Basic check to avoid false positives in random text
                    log("Found auth_permission table in CSV.")
                    in_permission_table = True
                    perm_header = row
                    continue

            if in_permission_table:
                # Check for end of table (another header)
                if 'id' in row and ('email' in row or 'password' in row or 'username' in row or 'key' in row or 'group_id' in row):
                    in_permission_table = False
                    continue

                if len(row) != len(perm_header):
                    # length mismatch
                    continue

                data = dict(zip(perm_header, row))

                old_perm_id = data.get('id')
                codename = data.get('codename')
                old_ct_id = data.get('content_type_id')

                # 1. Infer CT Map
                if codename and old_ct_id and old_ct_id not in source_ct_map:
                    parts = codename.split('_', 1)
                    if len(parts) == 2:
                         model_name = parts[1]
                         matching_ids = target_model_map.get(model_name)
                         if matching_ids:
                             source_ct_map[old_ct_id] = matching_ids[0] # taking first match

                # 2. Infer Perm Map
                if old_perm_id and codename and old_ct_id:
                     new_ct_id = source_ct_map.get(old_ct_id)
                     if new_ct_id:
                         key = (codename, new_ct_id)
                         if key in target_perm_map:
                             permission_id_map[old_perm_id] = target_perm_map[key]

    log(f"Mapped {len(source_ct_map)} ContentTypes and {len(permission_id_map)} Permissions.")
    return source_ct_map, permission_id_map

def run_import(csv_path):
    log("Building signature map...")
    sig_map = get_signature_map()
    log(f"Signature Map built with {len(sig_map)} models.")

    log("Scanning mappings...")
    ct_map, perm_map = scan_mappings(csv_path)

    current_model = None
    current_header = None

    # Counters
    success = 0
    errors = 0
    skips = 0

    log("Starting Main Import...")
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue

            sig = frozenset(row)
            if sig in sig_map:
                current_model = sig_map[sig]
                current_header = row
                log(f"--> Importing table for: {current_model._meta.label}")
                continue

            if not current_model or not current_header:
                skips += 1
                continue

            if len(row) != len(current_header):
                # Likely end of table or empty line between tables
                current_model = None
                current_header = None
                continue

            # Map data
            try:
                data = dict(zip(current_header, row))
            except Exception as e:
                log(f"Error zipping header/row: {e}")
                continue

            # CLEANUP & TRANSFORMS

            # 1. Skip auth.Permission and ContentType
            if current_model._meta.label in ['auth.Permission', 'contenttypes.ContentType']:
                continue

            # 2. Fix content_type_id
            if 'content_type_id' in data:
                old = data['content_type_id']
                if old in ct_map:
                    data['content_type_id'] = ct_map[old]
                else:
                    # Keep as is or handle error
                    pass

            # 3. Fix permission_id in auth_group_permissions
            if 'permission_id' in data and 'auth_group_permissions' in str(current_model._meta):
                old_p = data['permission_id']
                if old_p in perm_map:
                    data['permission_id'] = perm_map[old_p]
                else:
                    continue

            # 4. Handle NULLs
            for k, v in data.items():
                if v == '' or v == 'NULL':
                    data[k] = None
                elif v == 'True': data[k] = True
                elif v == 'False': data[k] = False

            try:
                # INSERT
                if 'id' in data:
                    pk = data['id']
                    current_model.objects.update_or_create(id=pk, defaults=data)
                else:
                    current_model.objects.get_or_create(**data)

                success += 1
                if success % 1000 == 0:
                    log(f"Imported {success} rows...")
            except Exception as e:
                # errors += 1
                # Only log first 10 errors to avoid spamming
                if errors < 10:
                    log(f"Error importing {current_model._meta.label}: {e}")
                errors += 1

    log(f"Done. Success: {success}, Errors: {errors}, Skips: {skips}")
    debug_file.close()

if __name__ == '__main__':
    run_import('sql_jawlasp_com.csv')
