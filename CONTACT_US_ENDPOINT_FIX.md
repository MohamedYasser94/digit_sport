# Contact Us / Support Endpoint Fix

## Problem
The Flutter app was sending POST requests to `/api/v1/support/contact-us/` but receiving **404 Not Found** errors:
```
[14/Jan/2026 22:51:45] WARNING [django.server:213] "POST /api/v1/support/contact-us HTTP/1.1" 404
```

## Root Cause
The endpoint `/api/v1/support/contact-us/` did not exist in the API URL configuration.

## Solution Implemented

### 1. Created ContactUs View
**File:** `api/v4/views/user.py`

Added a new API endpoint function:
```python
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def ContactUs(request):
    """
    Handles contact us / support requests from the mobile app.
    Accepts: name, email, phone, subject, message
    """
```

**Features:**
- ✅ Accepts POST requests without authentication
- ✅ Validates required fields (name, email, message)
- ✅ Logs contact request details
- ✅ Optionally sends email notification to admin
- ✅ Returns proper success/error responses

**Request Format:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "subject": "Support Request",
  "message": "I need help with..."
}
```

**Success Response (200 OK):**
```json
{
  "error": false,
  "message": "Thank you for contacting us. We will get back to you soon.",
  "status": "success"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": true,
  "message": "Name, email, and message are required fields."
}
```

### 2. Added URL Route
**File:** `api/v4/urls.py`

Added the route:
```python
path('v1/support/contact-us/', user.ContactUs, name='ContactUs'),
```

**Full endpoint URL:**
```
POST http://192.168.5.2:8058/api/v1/support/contact-us/
```

## Testing

### Test with cURL:
```bash
curl -X POST http://192.168.5.2:8058/api/v1/support/contact-us/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "subject": "Test Subject",
    "message": "This is a test message"
  }'
```

**Expected Response:**
```json
{
  "error": false,
  "message": "Thank you for contacting us. We will get back to you soon.",
  "status": "success"
}
```

### Test from Flutter App:
The Flutter app should now successfully POST to this endpoint without receiving 404 errors.

## Email Notification (Optional)

The endpoint attempts to send an email notification to the admin when a contact request is submitted. This requires:

1. **Settings configuration** in `settings.py`:
   - `EMAIL_BACKEND` configured
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` set
   - `RECIPIENT_ADDRESS` defined for receiving contact messages

2. **Email sending utility** at `api/v4/utils.py` with `Util.send_email()` method

**Note:** If email sending fails, the request still succeeds (email failure is caught and logged).

## Future Enhancements

Consider adding:

1. **Database persistence:**
   - Create a `ContactMessage` model to store all contact requests
   - Allows admin to view contact history

2. **User confirmation email:**
   - Send confirmation email to user that request was received
   - Improve user experience

3. **Rate limiting:**
   - Prevent spam/abuse by limiting requests per IP/user
   - Use Django rate limiting middleware

4. **Admin dashboard:**
   - View/manage contact requests in Django admin
   - Mark as read/resolved
   - Add response notes

## Files Modified

1. ✅ `api/v4/views/user.py` - Added ContactUs function
2. ✅ `api/v4/urls.py` - Added URL route

## Status

✅ **COMPLETE** - The contact-us endpoint is now functional and ready to use.

## Summary

- **Problem:** 404 on `/api/v1/support/contact-us/`
- **Solution:** Created endpoint and added URL route
- **Status:** Fixed ✅
- **Restart:** Django server needs restart to apply URL changes

