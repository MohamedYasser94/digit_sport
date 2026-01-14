# FCM Token Save Fix - Quick Reference

## Problem
❌ **400 Bad Request** when saving Firebase FCM tokens from Flutter app

## Root Cause
The `device_token` field in the `DeviceInfo` model had `max_length=100`, but Firebase FCM tokens are ~142 characters long. When the Flutter app tried to save a 142-character token, Django validation failed with a 400 error.

**Token Length:** 
```
dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw
= 142 characters (exceeds 100 character limit)
```

## Solution Applied

### 1. File: `api/v4/views/notification.py`
✅ Added missing `import json` at line 1
✅ Improved error handling with proper exception logging

### 2. File: `core/models/notifications.py`
✅ Changed line 81:
```python
# Before
device_token = models.CharField(max_length=100, null=True, blank=True)

# After
device_token = models.CharField(max_length=500, null=True, blank=True)
```

### 3. Database Migration
✅ Created: `core/migrations/0006_alter_deviceinfo_device_token.py`
✅ Applied migration automatically (successfully synced)

## Endpoint Fixed
```
POST /api/v3/devices/fcm/token/post/
```

## What Changed
| Aspect | Before | After |
|--------|--------|-------|
| Import | ❌ Missing | ✅ Added `import json` |
| Field Length | 100 chars | 500 chars |
| Error Logging | Poor | ✅ Detailed traceback |
| Validation | Silent fail | ✅ Explicit error messages |
| Migration | N/A | ✅ Applied `0006` |

## Status
✅ **READY TO TEST** - All changes applied and migration complete

## Next Steps
1. Restart Django server
2. Test with Flutter app to verify FCM token saves correctly
3. Check database to confirm DeviceInfo and FCMDevice records are created

## Commands to Verify
```bash
# Check migration status
python manage.py showmigrations core

# Verify field in database
python manage.py shell
from core.models.notifications import DeviceInfo
from django.db import connection
cursor = connection.cursor()
cursor.execute("DESCRIBE core_deviceinfo;")
# Look for: device_token | varchar(500)
```

## Files Modified
1. ✅ `api/v4/views/notification.py`
2. ✅ `core/models/notifications.py`
3. ✅ `core/migrations/0006_alter_deviceinfo_device_token.py` (auto-generated)

## Backwards Compatible
✅ Yes - Existing code continues to work, just accepts longer tokens now

