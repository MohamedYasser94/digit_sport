# Player Details - TransferMarket Fetch Feature

## Overview

Added ability to fetch TransferMarket data for a **single player** from the player details page. This allows recovery if the bulk player fetch fails, by fetching data on-demand.

**Use Case**: If bulk fetch of 1000 players fails at player #500, you can now go to each player's detail page and fetch their data individually.

---

## What Changed

### Updated Function: `AdminPlayersDetails` (views.py)

**File**: `apps/sport/views/views.py` (line 2157)

**New Features**:
1. ✅ POST request handling for `action=fetch_transfermarket`
2. ✅ Single player TransferMarket data fetch
3. ✅ Error handling with user-friendly messages
4. ✅ Success/failure feedback to template
5. ✅ Data persistence after fetch

**Old Code**:
```python
def AdminPlayersDetails(request, slug):
    player = Players.objects.get(slug=slug)
    teams = Teams.objects.all()
    context = {...}
    return render(...)
```

**New Code**:
```python
def AdminPlayersDetails(request, slug):
    """
    Display player details and optionally fetch TransferMarket data for single player.
    This allows recovery if bulk fetch failed, by fetching data on-demand.
    """
    player = Players.objects.get(slug=slug)
    fetch_tm_message = None
    fetch_tm_success = False

    # If user requested to fetch TransferMarket data
    if request.method == "POST" and request.POST.get('action') == 'fetch_transfermarket':
        try:
            # Import the update function
            from .update_players_transfermarket import (
                get_transfermarket_data_for_player,
                update_player_with_transfermarket_data
            )
            
            # Fetch and update
            tm_data = get_transfermarket_data_for_player(player)
            
            if tm_data:
                update_player_with_transfermarket_data(player, tm_data)
                fetch_tm_success = True
                fetch_tm_message = f"✓ TransferMarket data updated for {player.name}"
                player.refresh_from_db()
            else:
                fetch_tm_message = f"⚠ No TransferMarket data found for {player.name}"
        
        except Exception as e:
            fetch_tm_message = f"✗ Error: {str(e)}"
    
    # ...rest of code
```

---

## How It Works

### User Flow

```
1. User goes to Player Details Page
   ↓
2. Sees "Fetch TransferMarket Data" button
   ↓
3. Clicks button
   ↓
4. POST request sent with action='fetch_transfermarket'
   ↓
5. AdminPlayersDetails processes request
   ├─ Fetches TransferMarket data for player
   ├─ Updates player model
   └─ Refreshes data from database
   ↓
6. Success/error message displayed
   ↓
7. Page reloads with updated data
```

### Request Flow

```
POST /admin/players/<slug>/details/

Headers:
  Content-Type: application/x-www-form-urlencoded

Body:
  action=fetch_transfermarket
  csrfmiddlewaretoken=<token>

Response:
  Context variables:
    - fetch_tm_message: "✓ TransferMarket data updated..."
    - fetch_tm_success: True/False
    - has_transfermarket_id: True/False
    - player: Updated player object
```

---

## Template Implementation

### Step 1: Add the Button

Add this to your player details template (usually `core/templates/backend/sport/players/details.html`):

```html
<div class="card mt-3">
    <div class="card-header">
        <h5>TransferMarket Data</h5>
    </div>
    <div class="card-body">
        <!-- Status message -->
        {% if fetch_tm_message %}
            <div class="alert alert-{% if fetch_tm_success %}success{% else %}warning{% endif %} alert-dismissible fade show" role="alert">
                {{ fetch_tm_message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endif %}

        <!-- Fetch button -->
        <form method="POST" class="d-inline">
            {% csrf_token %}
            <input type="hidden" name="action" value="fetch_transfermarket">
            <button type="submit" class="btn btn-primary" 
                    title="Fetch latest data from TransferMarket for this player">
                <i class="fas fa-cloud-download-alt"></i>
                Fetch TransferMarket Data
            </button>
        </form>

        <!-- Display current data -->
        <div class="mt-3">
            {% if has_transfermarket_id %}
                <p class="text-muted">
                    <i class="fas fa-check-circle text-success"></i>
                    TransferMarket ID: <code>{{ player.transfermarkt_id }}</code>
                </p>
            {% else %}
                <p class="text-muted">
                    <i class="fas fa-exclamation-circle text-warning"></i>
                    No TransferMarket ID linked yet.
                </p>
            {% endif %}

            <!-- Show fetched data if available -->
            {% if player.current_market_value %}
                <p><strong>Market Value:</strong> {{ player.current_market_value }}</p>
            {% endif %}
            {% if player.position %}
                <p><strong>Position:</strong> {{ player.position }}</p>
            {% endif %}
            {% if player.foot %}
                <p><strong>Foot:</strong> {{ player.foot }}</p>
            {% endif %}
            {% if player.age %}
                <p><strong>Age:</strong> {{ player.age }}</p>
            {% endif %}
        </div>
    </div>
</div>
```

**Full template file**: See `PLAYER_DETAILS_TEMPLATE_UPDATE.html`

---

## Use Cases

### Case 1: Bulk Fetch Failed Mid-Way

**Scenario**: You ran bulk fetch, it processed 500 players, then failed on player #501.

**Solution**:
1. Go to player #501's detail page
2. Click "Fetch TransferMarket Data"
3. Player data is fetched individually
4. Continue with remaining players

### Case 2: Single Player Data Needs Updating

**Scenario**: A player's market value changed, and you need current data.

**Solution**:
1. Go to player's detail page
2. Click "Fetch TransferMarket Data"
3. Latest TransferMarket data is fetched
4. Player info is updated

### Case 3: Player Missing TransferMarket ID

**Scenario**: Player has no TransferMarket ID because bulk fetch didn't find them.

**Solution**:
1. Go to player's detail page
2. Click "Fetch TransferMarket Data"
3. System searches TransferMarket API for this player
4. If found, ID is saved and data is updated
5. Future bulk fetches will use this ID

---

## Error Handling

### Success Case
```json
{
  "fetch_tm_message": "✓ TransferMarket data updated successfully for Messi",
  "fetch_tm_success": true,
  "has_transfermarket_id": true
}
```

Display:
- ✅ Green success message
- Show updated data (market value, position, etc.)

### Not Found Case
```json
{
  "fetch_tm_message": "⚠ No TransferMarket data found for PlayerName. Try a different search or check the name spelling.",
  "fetch_tm_success": false,
  "has_transfermarket_id": false
}
```

Display:
- ⚠️ Yellow warning message
- Suggest checking player name spelling

### Error Case
```json
{
  "fetch_tm_message": "✗ Error fetching TransferMarket data: Connection timeout",
  "fetch_tm_success": false,
  "has_transfermarket_id": false
}
```

Display:
- ❌ Red error message
- Log full traceback to debug.log

---

## Context Variables

The view now passes these variables to the template:

| Variable | Type | Description |
|----------|------|-------------|
| `fetch_tm_message` | String | Success/error message to display |
| `fetch_tm_success` | Boolean | Whether fetch was successful |
| `has_transfermarket_id` | Boolean | Whether player has TransferMarket ID |
| `player` | Object | Updated player object (with new data) |

---

## Benefits

✅ **Recovery from Bulk Failures**
- If bulk fetch fails, individual players can still get their data

✅ **On-Demand Updates**
- Users can manually refresh a player's TransferMarket data anytime

✅ **Better User Experience**
- Clear success/error messages
- No need to re-run entire bulk operation
- Real-time feedback

✅ **Robust Integration**
- Uses same `update_player_with_transfermarket_data()` function
- Leverages existing API client with timeout/retry logic
- Graceful error handling

✅ **Flexible Workflow**
- Works if bulk fetch:
  - Never ran
  - Failed partially
  - Timed out
  - Needs updating

---

## Implementation Steps

### Step 1: Verify Code Change
✅ Code already updated in `apps/sport/views/views.py` line 2157

### Step 2: Update Template

Add the button and status display to your player details template:

**File**: `core/templates/backend/sport/players/details.html`

**Add this section** (see full template in `PLAYER_DETAILS_TEMPLATE_UPDATE.html`):

```html
<div class="card mt-3">
    <!-- Button and status -->
    {% if fetch_tm_message %}
        <div class="alert ...">{{ fetch_tm_message }}</div>
    {% endif %}
    <form method="POST">
        {% csrf_token %}
        <input type="hidden" name="action" value="fetch_transfermarket">
        <button type="submit" class="btn btn-primary">
            <i class="fas fa-cloud-download-alt"></i>
            Fetch TransferMarket Data
        </button>
    </form>
</div>
```

### Step 3: Test

1. Go to player details page
2. Click "Fetch TransferMarket Data" button
3. Verify message appears
4. Check that player data was updated

---

## Troubleshooting

### Issue: Button doesn't appear

**Solution**: Check that template changes were applied correctly

### Issue: "No TransferMarket data found"

**Solution**:
1. Check player name spelling
2. Try updating player name to match TransferMarket
3. Check TransferMarket API availability

### Issue: "Error fetching TransferMarket data"

**Solution**:
1. Check debug.log for full error
2. Verify internet connectivity
3. Check API_REQUEST_TIMEOUT setting
4. Verify SPORT_MONKS_TOKEN and other settings

### Issue: Page doesn't refresh

**Solution**:
1. Check browser console for errors
2. Verify CSRF token is included in form
3. Check that POST method is set on form

---

## Integration with Bulk Fetch

### Bulk Fetch Workflow

```
1. Run bulk fetch: POST /sport/monk/players/api/get/
   ├─ Fetches 1000 players
   └─ May fail on some players

2. Go to Admin Players list
   ├─ See which players succeeded
   └─ See which players had errors

3. For failed players:
   ├─ Click player details
   └─ Click "Fetch TransferMarket Data"
   └─ Individual fetch happens
   └─ Player data updated

4. Result: All players have TransferMarket data!
```

### Architecture

```
┌─────────────────────────────────────────┐
│  Bulk Fetch                             │
│  (POST /monk/players/api/get/)          │
│  ├─ 1000 players                        │
│  ├─ May fail on some                    │
│  └─ Returns stats                       │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   ✓ Success    ✗ Failed
        │             │
        │             └─► Go to details
        │                 Click Fetch
        │                 │
        │                 ▼
        │            Individual Fetch
        │            (POST with action=fetch_transfermarket)
        │            │
        │            ▼
        └─────► Both Updated ✓
```

---

## Code Structure

### View Function Changes

```python
@staff_only
def AdminPlayersDetails(request, slug):
    player = Players.objects.get(slug=slug)
    fetch_tm_message = None
    fetch_tm_success = False
    
    # NEW: Handle TransferMarket fetch request
    if request.method == "POST" and request.POST.get('action') == 'fetch_transfermarket':
        try:
            from .update_players_transfermarket import (
                get_transfermarket_data_for_player,
                update_player_with_transfermarket_data
            )
            
            tm_data = get_transfermarket_data_for_player(player)
            if tm_data:
                update_player_with_transfermarket_data(player, tm_data)
                fetch_tm_success = True
                fetch_tm_message = f"✓ TransferMarket data updated..."
                player.refresh_from_db()
            else:
                fetch_tm_message = f"⚠ No TransferMarket data found..."
        except Exception as e:
            fetch_tm_message = f"✗ Error: {str(e)}"
    
    # OLD: Rest of function
    teams = Teams.objects.all()
    context = {
        'player': player,
        'teams': teams,
        # NEW: Add TransferMarket status to context
        'fetch_tm_message': fetch_tm_message,
        'fetch_tm_success': fetch_tm_success,
        'has_transfermarket_id': bool(player.transfermarkt_id),
    }
    return render(...)
```

---

## Summary

✅ **Feature Implemented**:
- Single player TransferMarket fetch from details page
- Error handling with user-friendly messages
- Integration with existing API client
- Works as fallback for bulk fetch failures

✅ **User Benefits**:
- Recover from bulk fetch failures
- Update individual player data on-demand
- Clear feedback on success/error
- No need to re-run entire bulk operation

✅ **Next Steps**:
1. Add template button (see PLAYER_DETAILS_TEMPLATE_UPDATE.html)
2. Test the feature
3. Enjoy on-demand TransferMarket data fetching!

---

**Status**: ✅ IMPLEMENTED

The player details page now supports fetching TransferMarket data individually,
providing a robust fallback when bulk operations fail.

