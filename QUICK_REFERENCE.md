# TransferMarket Integration - Quick Reference Card

## 🚀 3-Step Quick Start

```bash
# 1. Run Migration
python manage.py migrate sport

# 2. Edit this function with your data source
# File: apps/sport/views/update_players_transfermarket.py
# Function: load_transfermarket_data()

# 3. Use admin UI to update players
# Button: "Update Players From Transfermarket"
```

---

## 📋 Essential Commands

```bash
# Run migration
python manage.py migrate sport

# Test data loading
python apps/sport/examples/transfermarket_integration_examples.py

# Migrate from MultiSourcePlayers (if needed)
python manage.py migrate_multisource_players --dry-run
python manage.py migrate_multisource_players --sport=football

# Check migration status
python manage.py showmigrations sport
```

---

## 🔑 Key Concepts

### Data Sources Priority
```
1. Sportmonks → Primary (api_id, team, league) → For Flutter app
2. TransferMarket → Update (values, images, stats) → For enrichment
3. Manual → Protected (name_tr only) → Never auto-update
```

### Field Protection
```
🔒 NEVER Updated: name_tr, api_id, team, league
✅ ALWAYS Updated: market_value, images, physical stats
⚠️ IF EMPTY: name, position, birthdate
```

### Matching Strategy
```
1. TransferMarket ID → 100% accurate
2. Name + Team → 80% threshold
3. Name Only → 85% threshold (fallback)
```

---

## 📁 Important Files

### Documentation (Read These First)
```
DOCUMENTATION_INDEX.md ← Start here
TRANSFERMARKET_QUICKSTART.md ← Follow this
TRANSFERMARKET_VISUAL_GUIDE.md ← Visual understanding
TRANSFERMARKET_INTEGRATION.md ← Detailed guide
```

### Implementation Files (Edit These)
```
apps/sport/views/update_players_transfermarket.py
  └─ Function to edit: load_transfermarket_data()

apps/sport/examples/transfermarket_integration_examples.py
  └─ Copy integration method from here
```

---

## 🔧 Configuration Template

```python
# File: apps/sport/views/update_players_transfermarket.py
# Function: load_transfermarket_data()

def load_transfermarket_data():
    import os
    import json
    from django.conf import settings
    
    # Method 1: JSON File (Most Common)
    data_file = os.path.join(
        settings.BASE_DIR, 
        'scraped_data',  # Your folder
        'transfermarket_players.json'  # Your file
    )
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []
```

---

## 📊 Required Data Format

```json
{
    "name": "Player Name",
    "href": "/player-name/profil/spieler/12345",
    "image_url": "https://...",
    "current_market_value": "€50.00m",
    "age": "25",
    "position": "Centre-Forward",
    "height": "1.85m",
    "foot": "right",
    "current_club": {"name": "Team Name"}
}
```

**Minimum Required:** `name`  
**Recommended:** `name`, `current_market_value`, `position`, `image_url`

---

## ✅ Pre-Flight Checklist

Before running update:
- [ ] Migration completed
- [ ] Data source configured
- [ ] Test data loads successfully
- [ ] Database backed up
- [ ] Understand what gets updated

---

## 🎯 Quick Troubleshooting

### No players updated?
```
1. Check load_transfermarket_data() returns data
2. Print/log the data to verify format
3. Test with exact name match first
4. Verify file path is correct
```

### Wrong matches?
```
1. Increase threshold (default 80%)
2. Add manual transfermarkt_id for VIP players
3. Verify team names match
```

### Market values not parsing?
```
1. Check format: €50.00m, $25M, £30m
2. Verify currency symbol (€, $, £, ¥)
3. Check multiplier (m, bn, k)
```

---

## 📈 Expected Results

| Metric | Target |
|--------|--------|
| Match Rate | 85-95% |
| Processing Time | 2-5 min per 1000 players |
| Data Completeness | 90%+ |
| Overwrites | 0 (name_tr, api_id) |

---

## 🔍 Quick Test

```python
# Test in Django shell
from apps.sport.views.update_players_transfermarket import load_transfermarket_data

data = load_transfermarket_data()
print(f"Loaded {len(data)} players")
if data:
    print("Sample:", data[0])
```

---

## 🎓 Learning Path

```
5 min:  Read IMPLEMENTATION_COMPLETE.md
10 min: Read TRANSFERMARKET_VISUAL_GUIDE.md
30 min: Follow TRANSFERMARKET_QUICKSTART.md
        └─ Run migration
        └─ Configure data source
        └─ Test with 5 players
As needed: Reference TRANSFERMARKET_INTEGRATION.md
```

---

## 📞 Help Resources

| Issue | Document | Section |
|-------|----------|---------|
| Getting started | QUICKSTART | Steps 1-4 |
| Data format | INTEGRATION | Data Format |
| Matching | VISUAL GUIDE | Matching Algorithm |
| Code examples | examples.py | All methods |
| Troubleshooting | QUICKSTART | Troubleshooting |

---

## 🌟 Key Features

✅ Single Players model (not MultiSourcePlayers)  
✅ Sportmonks primary (Flutter compatible)  
✅ TransferMarket enrichment (values, images)  
✅ Protected fields (name_tr never updated)  
✅ Smart matching (fuzzy algorithm)  
✅ Safe updates (no data loss)  
✅ Progress tracking (real-time UI)  
✅ Well documented (5 comprehensive guides)  

---

## 🎯 Success Criteria

You're ready when:
- [x] Migration run successfully
- [x] Data source returns data
- [x] Test update works with 5 players
- [x] Market values populated
- [x] Images loaded
- [x] name_tr preserved
- [x] api_id unchanged

---

## 📝 Quick Notes

**Project:** digit_sport  
**Date:** December 15, 2025  
**Migration:** 0003_add_transfermarket_fields_to_players  
**Status:** ✅ Ready for Production  

**Protected Fields:** name_tr, api_id, team, league  
**Updated Fields:** market_value, image_url, height, weight, foot, contract, agent  
**Flutter Compatible:** Yes (api_id preserved)  

---

**Print this card and keep it handy during implementation!**

