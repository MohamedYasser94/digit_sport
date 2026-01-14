# User Registration Fix - Token Import Error

## Problem
The user registration endpoint was returning:
```
500 Internal Server Error
"Error creating user: type object 'Token' has no attribute 'objects'"
```

When Flutter app sent a POST request to:
```
POST /api/auth/signup/register/
```

## Root Cause
The import statement in `api/v4/views/user.py` was importing the wrong `Token` class:

**WRONG (before):**
```python
from rest_framework_simplejwt.tokens import RefreshToken, Token
```

The `Token` from `rest_framework_simplejwt` is a JWT token class that doesn't have an ORM `.objects` manager.

**The code tried to do this:**
```python
token, created = Token.objects.get_or_create(user=user)
```

But `Token` from `rest_framework_simplejwt` doesn't support `.objects.get_or_create()`.

## Solution
Changed the import to use the correct `Token` class from Django REST Framework's authtoken app:

**CORRECT (after):**
```python
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
```

Now:
- ✅ `Token` has the `.objects` manager for database operations
- ✅ `RefreshToken` is used for JWT token generation
- ✅ Both serve their proper purposes

## Files Modified
**File:** `api/v4/views/user.py`
- Line 2: Added `import json` (was missing)
- Line 6: Added `authenticate` to imports
- Line 17: Changed `Token` import to `rest_framework.authtoken.models`
- Line 21: Kept `RefreshToken` import separate from `rest_framework_simplejwt.tokens`

## Testing
After the fix, the user registration endpoint should:

1. Accept POST request with:
```json
{
  "first_name": "sadsa",
  "last_name": "sads",
  "email": "ad@gmail.com",
  "password": "3432432"
}
```

2. Return 201 Created:
```json
{
  "error": false,
  "message": "User created successfully",
  "data": {...user details...},
  "token": "...auth token..."
}
```

## How to Verify
```bash
# Test the registration endpoint
curl -X POST http://192.168.5.2:8058/api/auth/signup/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "password123"
  }'

# Expected: 201 Created with user data and token
```

## Summary
✅ **Fixed:** Incorrect Token import causing `.objects` AttributeError
✅ **Status:** User registration should now work properly
✅ **No breaking changes:** Just using the correct import

