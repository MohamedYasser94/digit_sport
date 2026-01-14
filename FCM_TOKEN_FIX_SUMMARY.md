# FCM Token Save Fix - Summary

## Problem Identified
The Flutter app was receiving a **400 Bad Request** error when trying to save FCM (Firebase Cloud Messaging) tokens. The error occurred at the endpoint:
```
http://192.168.5.2:8058/api/v3/devices/fcm/token/post/
```

## Root Causes

### 1. **Missing JSON Import** ❌ FIXED
**File:** `api/v4/views/notification.py`
- The `json` module was used (`json.loads()`) but not imported
- This would cause a `NameError` when trying to parse JSON request body

### 2. **Inadequate Error Handling** ❌ FIXED
**File:** `api/v4/views/notification.py` 
- Exceptions were caught but not properly logged with traceback information
- This made debugging difficult when validation failures occurred
- Added proper error logging with traceback and descriptive error messages

### 3. **Device Token Field Length Too Short** ❌ FIXED (MAIN ISSUE)
**File:** `core/models/notifications.py`
- The `device_token` field had `max_length=100`
- Firebase FCM tokens are typically 142+ characters long
- The test token provided: `dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw` = **142 characters**
- This caused validation to fail silently, resulting in 400 errors

## Changes Made

### 1. Added Missing Import
```python
# api/v4/views/notification.py - Line 1
import json
```

### 2. Improved Error Handling
```python
# api/v4/views/notification.py - DeviceFcmAdd function
- Added try-except block around json.loads() with specific JSONDecodeError handling
- Added validation for required 'device_token' field before processing
- Added descriptive error messages in responses
- Added traceback printing for debugging
```

### 3. Increased Device Token Field Length
```python
# core/models/notifications.py - Line 81
# Before:
device_token = models.CharField(max_length=100, null=True, blank=True)

# After:
device_token = models.CharField(max_length=500, null=True, blank=True)
```

### 4. Applied Database Migration
```bash
python manage.py makemigrations
# Output: core/migrations/0006_alter_deviceinfo_device_token.py

python manage.py migrate
# Output: Applying core.0006_alter_deviceinfo_device_token... OK
```

## Testing the Fix

To test the fix with the provided FCM token:

```bash
curl -X POST http://192.168.5.2:8058/api/v3/devices/fcm/token/post/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw",
    "device_type": "Android",
    "device_info": "Device information"
  }'
```

**Expected Response (201 Created):**
```json
{
  "status": "success",
  "message": "Device Info saved successfully",
  "device_token": "dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw",
  "device_code": "XXXXX"
}
```

## Files Modified
1. ✅ `api/v4/views/notification.py` - Added json import and improved error handling
2. ✅ `core/models/notifications.py` - Increased device_token max_length to 500
3. ✅ `core/migrations/0006_alter_deviceinfo_device_token.py` - Database migration (auto-generated)

## Benefits
- ✅ Firebase FCM tokens are now properly stored (up to 500 characters)
- ✅ Better error logging for debugging future issues
- ✅ Proper JSON parsing with exception handling
- ✅ Validation feedback to the client
- ✅ All changes are backward compatible

## Notes
- The `device_token` field now supports tokens up to 500 characters (safe margin for future variations)
- FCM tokens have been stable at ~142 characters, but the extra space provides future-proofing
- No breaking changes to existing functionality

