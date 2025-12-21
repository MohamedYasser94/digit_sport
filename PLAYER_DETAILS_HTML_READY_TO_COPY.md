# Ready-to-Use HTML Code for Player Details Template

## Copy-Paste Ready HTML

Copy this entire HTML block and paste it into your player details template:

```html
<!-- TransferMarket Data Section -->
<div class="card mt-3">
    <div class="card-header">
        <h5 class="mb-0">
            <i class="fas fa-exchange-alt"></i>
            TransferMarket Data
        </h5>
    </div>
    <div class="card-body">
        <!-- Status Messages -->
        {% if fetch_tm_message %}
            <div class="alert alert-{% if fetch_tm_success %}success{% else %}warning{% endif %} alert-dismissible fade show" role="alert">
                <strong>
                    {% if fetch_tm_success %}
                        <i class="fas fa-check-circle"></i> Success
                    {% else %}
                        <i class="fas fa-exclamation-triangle"></i> Status
                    {% endif %}
                </strong>
                {{ fetch_tm_message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        {% endif %}

        <!-- Fetch Button -->
        <form method="POST" class="mb-3">
            {% csrf_token %}
            <input type="hidden" name="action" value="fetch_transfermarket">
            <button type="submit" class="btn btn-primary" title="Fetch latest data from TransferMarket for this player">
                <i class="fas fa-cloud-download-alt"></i>
                Fetch TransferMarket Data
            </button>
        </form>

        <!-- Current TransferMarket Status -->
        <div class="row">
            <div class="col-md-6">
                <h6 class="border-bottom pb-2">Status</h6>
                {% if has_transfermarket_id %}
                    <p>
                        <span class="badge bg-success">
                            <i class="fas fa-check-circle"></i>
                            Linked
                        </span>
                    </p>
                    <p class="mb-0">
                        <small class="text-muted">TransferMarket ID:</small><br>
                        <code>{{ player.transfermarkt_id }}</code>
                    </p>
                {% else %}
                    <p>
                        <span class="badge bg-warning">
                            <i class="fas fa-exclamation-circle"></i>
                            Not Linked
                        </span>
                    </p>
                    <p class="mb-0">
                        <small class="text-muted">Click above to search and link.</small>
                    </p>
                {% endif %}
            </div>

            <!-- TransferMarket Data Display -->
            <div class="col-md-6">
                <h6 class="border-bottom pb-2">Player Data</h6>
                
                {% if player.current_market_value %}
                    <p class="mb-2">
                        <strong><i class="fas fa-euro-sign text-warning"></i> Market Value:</strong><br>
                        <code>{{ player.current_market_value }}</code>
                    </p>
                {% endif %}

                {% if player.position %}
                    <p class="mb-2">
                        <strong><i class="fas fa-futbol text-info"></i> Position:</strong><br>
                        {{ player.position }}
                    </p>
                {% endif %}

                {% if player.age %}
                    <p class="mb-2">
                        <strong><i class="fas fa-birthday-cake"></i> Age:</strong><br>
                        {{ player.age }}
                    </p>
                {% endif %}

                {% if player.foot %}
                    <p class="mb-2">
                        <strong><i class="fas fa-shoe-prints"></i> Preferred Foot:</strong><br>
                        {{ player.foot }}
                    </p>
                {% endif %}

                {% if player.citizenship %}
                    <p class="mb-2">
                        <strong><i class="fas fa-flag"></i> Citizenship:</strong><br>
                        {{ player.citizenship }}
                    </p>
                {% endif %}

                {% if player.contract_expires %}
                    <p class="mb-0">
                        <strong><i class="fas fa-calendar-times text-danger"></i> Contract Expires:</strong><br>
                        {{ player.contract_expires }}
                    </p>
                {% endif %}
            </div>
        </div>

        <!-- Help Text -->
        <div class="alert alert-info mt-3 mb-0" role="alert">
            <small>
                <i class="fas fa-lightbulb"></i>
                <strong>Tip:</strong> 
                Use this to fetch TransferMarket data for individual players. 
                This is especially useful if the bulk fetch failed or if you need the latest data for this player.
            </small>
        </div>
    </div>
</div>
```

---

## Where to Add This Code

### Option 1: Add to Player Details Page
**File**: `core/templates/backend/sport/players/details.html`

**Location**: Add this block:
- After the player form fields
- Before the save button
- Or in a new tab/section

**Example placement**:
```html
<form method="POST">
    <!-- Existing player form fields -->
    <div class="form-group">
        <label>Name</label>
        <input type="text" name="name" value="{{ player.name }}">
    </div>
    
    <!-- ... more form fields ... -->
    
    <!-- ADD THE HTML BLOCK HERE -->
    <div class="card mt-3">
        <div class="card-header">
            <h5>TransferMarket Data</h5>
        </div>
        <!-- ... -->
    </div>
    
    <!-- Form buttons -->
    <button type="submit" class="btn btn-primary">Save</button>
</form>
```

### Option 2: Add to a Separate Tab
If you have tabs in the details page:

```html
<ul class="nav nav-tabs">
    <li class="nav-item">
        <a class="nav-link active" data-bs-toggle="tab" href="#details">Details</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#transfermarket">TransferMarket</a>
    </li>
</ul>

<div class="tab-content">
    <div id="details" class="tab-pane fade show active">
        <!-- Existing player form -->
    </div>
    
    <div id="transfermarket" class="tab-pane fade">
        <!-- ADD THE HTML BLOCK HERE -->
        <div class="card mt-3">
            <!-- ... -->
        </div>
    </div>
</div>
```

---

## How to Use

### For Admin Users:

1. **Navigate to Player Details**
   - Go to Admin Dashboard
   - Click on "Players"
   - Click on any player to view details

2. **Look for "TransferMarket Data" Section**
   - You'll see the new section on the page
   - Shows current TransferMarket status
   - Displays any linked TransferMarket data

3. **Click "Fetch TransferMarket Data" Button**
   - Button is blue with cloud icon
   - Click to fetch data for this player

4. **Wait for Response**
   - If successful: Green alert with "✓ TransferMarket data updated..."
   - If not found: Yellow alert with "⚠ No TransferMarket data found..."
   - If error: Red alert with error details

5. **View Updated Data**
   - Market value, position, age, foot, citizenship, contract expiry all updated
   - Data is immediately saved to database

---

## Customization

### Change Button Text
```html
<button type="submit" class="btn btn-primary">
    <i class="fas fa-sync-alt"></i>
    Update from TransferMarket
</button>
```

### Change Button Color
```html
<!-- Blue (Primary) - Default -->
<button class="btn btn-primary">...</button>

<!-- Green (Success) -->
<button class="btn btn-success">...</button>

<!-- Orange (Warning) -->
<button class="btn btn-warning">...</button>

<!-- Red (Danger) -->
<button class="btn btn-danger">...</button>
```

### Change Alert Style
```html
<!-- Success (Green) -->
<div class="alert alert-success">...</div>

<!-- Warning (Yellow) -->
<div class="alert alert-warning">...</div>

<!-- Info (Blue) -->
<div class="alert alert-info">...</div>

<!-- Danger (Red) -->
<div class="alert alert-danger">...</div>
```

### Hide Certain Fields
```html
<!-- If you don't want to show Market Value, remove or comment: -->
{% if player.current_market_value %}
    <p>
        <strong>Market Value:</strong>
        {{ player.current_market_value }}
    </p>
{% endif %}
```

---

## Bootstrap Classes Used

If your site uses Bootstrap, these classes will style automatically:

- `card` - Container box
- `card-header` - Title area
- `card-body` - Content area
- `btn btn-primary` - Blue button
- `alert alert-success` - Green alert
- `alert alert-warning` - Yellow alert
- `badge bg-success` - Green badge
- `row` / `col-md-6` - Two-column layout
- `fas fa-*` - Font Awesome icons

If your site uses different CSS framework (Tailwind, Materialize, etc.), you may need to adjust classes.

---

## Quick Implementation Checklist

- [ ] Find your `details.html` template file
- [ ] Copy the HTML code above
- [ ] Paste it into the template at an appropriate location
- [ ] Test it by going to a player detail page
- [ ] Click "Fetch TransferMarket Data" button
- [ ] Verify success message appears
- [ ] Check that player data was updated

---

## Testing

### Test 1: Successful Fetch
1. Go to player details
2. Click button
3. Expect: Green "✓ TransferMarket data updated..." message
4. Expect: Data fields populated (market value, position, etc.)

### Test 2: Player Not Found
1. Go to player details
2. Edit player name to something unusual
3. Click button
4. Expect: Yellow "⚠ No TransferMarket data found..." message
5. Expect: No data changes

### Test 3: Already Linked
1. Go to player that already has TransferMarket ID
2. Click button
3. Expect: Green success message
4. Expect: Data refreshed from TransferMarket

---

## Files Reference

- **View Code**: `apps/sport/views/views.py` (line 2157)
- **This HTML**: Copy-paste ready code above
- **Full Template Example**: `PLAYER_DETAILS_TEMPLATE_UPDATE.html`
- **Implementation Guide**: `PLAYER_DETAILS_FETCH_IMPLEMENTATION.md`
- **Quick Start**: `PLAYER_DETAILS_QUICK_START.md`

---

## Support

If you have issues:

1. Check that POST method is set on form
2. Verify CSRF token is included
3. Check browser console for errors
4. Check `debug.log` for backend errors
5. Verify TransferMarket API is working

All error details will be logged to `debug.log` for debugging.

---

**Ready to add to your template!** ✅

