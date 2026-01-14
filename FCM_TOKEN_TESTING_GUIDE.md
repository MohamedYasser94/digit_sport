# Testing the FCM Token Fix

## API Endpoint
```
POST /api/v3/devices/fcm/token/post/
```

## Request Headers
```
Content-Type: application/json
```

## Request Body
```json
{
  "device_token": "dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw",
  "device_type": "Android",
  "device_info": {"key": "value"}
}
```

## cURL Command
```bash
curl -X POST http://192.168.5.2:8058/api/v3/devices/fcm/token/post/ \
  -H "Content-Type: application/json" \
  -d '{"device_token":"dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw","device_type":"Android","device_info":{}}'
```

## Expected Success Response (201 Created)
```json
{
  "status": "success",
  "message": "Device Info saved successfully",
  "device_token": "dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw",
  "device_code": "XXXXX"
}
```

## Expected Success Response - Duplicate Token (200 OK)
If the token already exists in the database:
```json
{
  "status": "success",
  "message": "Device token already registered"
}
```

## Error Responses

### Missing device_token (400 Bad Request)
```json
{
  "error": "device_token is required"
}
```

### Invalid JSON (400 Bad Request)
```json
{
  "error": "Invalid JSON"
}
```

### Invalid HTTP Method (400 Bad Request)
```json
{
  "error": "Method not allowed"
}
```

### Server Error (400 Bad Request)
```json
{
  "error": "Error message describing what went wrong"
}
```

## Verification Steps

1. **Check device was created:**
   ```bash
   python manage.py shell
   >>> from core.models.notifications import DeviceInfo
   >>> DeviceInfo.objects.filter(device_token="dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw").exists()
   True
   ```

2. **Check FCM device was created:**
   ```bash
   python manage.py shell
   >>> from fcm_django.models import FCMDevice
   >>> FCMDevice.objects.filter(registration_id="dodLGcOERhOkU5SBbC6Tgg:APA91bG7pFXz2WC6v5p3XNcFQOPXSzxDWgsGs0kxSlQQT6saRpb9I56v9-UvI05dBQ0ofapxR83kQVUFQ5v-OCDiNuTcWAaAwojwpLRLue9rN5sf-pneOTw").exists()
   True
   ```

3. **Check database field length:**
   ```bash
   python manage.py shell
   >>> from django.db import connection
   >>> cursor = connection.cursor()
   >>> cursor.execute("DESCRIBE core_deviceinfo;")
   # Look for device_token field with varchar(500)
   ```

## What Was Fixed

✅ **Added missing `json` import** - Now properly parses JSON request body
✅ **Improved error handling** - Better error messages and logging  
✅ **Increased `device_token` field length** - Now supports 500 characters (FCM tokens are ~142 chars)
✅ **Applied database migration** - Schema updated successfully

## Flutter App Testing

In your Flutter app, you should now be able to:

```dart
// Register device token
final response = await Dio().post(
  'http://192.168.5.2:8058/api/v3/devices/fcm/token/post/',
  data: {
    'device_token': firebaseToken,
    'device_type': 'Android', // or 'iOS'
    'device_info': {},
  },
);

// Should now return 201 Created instead of 400 Bad Request
print(response.statusCode); // 201
```

## Troubleshooting

If you still get 400 errors:

1. **Check the server logs:**
   ```bash
   # Look for stack traces in the Django console/logs
   # The DeviceFcmAdd function now prints detailed error information
   ```

2. **Verify database migration was applied:**
   ```bash
   python manage.py showmigrations core
   # Should show 0006_alter_deviceinfo_device_token as [X] (applied)
   ```

3. **Check if there's an existing device with the same token:**
   - The endpoint checks for existing tokens and returns 200 OK if found
   - To re-register, you may need to delete the old entry

4. **Enable debug mode:**
   ```python
   # In settings.py, set DEBUG = True to see detailed error responses
   ```

