# TransferMarket Integration - Visual Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FLUTTER APP                             │
│                     (Uses Sportmonks API)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Uses api_id from Sportmonks
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PLAYERS MODEL (Main)                       │
│                                                                 │
│  PRIMARY SOURCE: Sportmonks (api_id, team, league)            │
│  UPDATE SOURCE:  TransferMarket (images, values, details)      │
│  MANUAL ONLY:    name_tr (Turkish name)                        │
└──────────────────────┬──────────────────┬──────────────────────┘
                       │                  │
          ┌────────────┴────────┐    ┌───┴────────────────┐
          │                     │    │                    │
          ▼                     ▼    ▼                    ▼
┌──────────────────┐   ┌────────────────────┐   ┌─────────────────┐
│ Sportmonks API   │   │ TransferMarket     │   │ Manual Entry    │
│                  │   │ Scraping           │   │ (Admin Panel)   │
│ - api_id        │   │ - market_value     │   │ - name_tr       │
│ - team          │   │ - image_url        │   │ - custom data   │
│ - league        │   │ - height/weight    │   │                 │
│ - match data    │   │ - foot             │   │                 │
└──────────────────┘   │ - contract info    │   └─────────────────┘
                       │ - agent            │
                       └────────────────────┘
```

## Data Flow Diagram

```
STEP 1: Initial Player Creation (from Sportmonks)
═══════════════════════════════════════════════════

┌─────────────────┐
│ Sportmonks API  │
│ Player Data     │
└────────┬────────┘
         │
         │ 1. Fetch player via "Fetch Players From API"
         ▼
┌──────────────────────────────────────┐
│ Player Created in Database           │
│                                      │
│ ✓ api_id = 12345 (Sportmonks)      │
│ ✓ name = "Mohamed Salah"            │
│ ✓ team = Liverpool FC               │
│ ✓ league = Premier League           │
│ ✓ position = Forward                │
│ ✗ market_value = (empty)            │
│ ✗ image_url = (empty)               │
│ ✗ transfermarkt_id = (empty)        │
└──────────────────────────────────────┘


STEP 2: Update with TransferMarket Data
════════════════════════════════════════

┌────────────────────┐
│ TransferMarket     │
│ Scraped Data       │
└─────────┬──────────┘
          │
          │ 2. Click "Update Players From Transfermarket"
          ▼
┌───────────────────────────────────────┐
│ Smart Matching Algorithm              │
│                                       │
│ 1. Match by name + team (80%)        │
│ 2. Find: "Mohamed Salah" + "Liverpool"│
│ 3. Confidence: 95% ✓                 │
└───────────┬───────────────────────────┘
            │
            │ 3. Update player fields
            ▼
┌──────────────────────────────────────┐
│ Player Updated in Database           │
│                                      │
│ ✓ api_id = 12345 (unchanged)       │
│ ✓ name = "Mohamed Salah" (unchanged)│
│ ✓ team = Liverpool FC (unchanged)   │
│ ✓ market_value = €65.00m (NEW!)    │
│ ✓ image_url = https://... (NEW!)   │
│ ✓ transfermarkt_id = 148455 (NEW!) │
│ ✓ height = 1.75m (NEW!)            │
│ ✓ foot = Left (NEW!)               │
│ ✗ name_tr = (still empty, manual)  │
└──────────────────────────────────────┘


STEP 3: Manual Turkish Name Entry
══════════════════════════════════

┌───────────────────┐
│ Admin manually    │
│ adds Turkish name │
└─────────┬─────────┘
          │
          │ 4. Admin edits player
          ▼
┌──────────────────────────────────────┐
│ Player Fully Updated                 │
│                                      │
│ ✓ api_id = 12345                    │
│ ✓ name = "Mohamed Salah"            │
│ ✓ name_tr = "محمد صلاح" (Manual!)  │
│ ✓ team = Liverpool FC               │
│ ✓ market_value = €65.00m            │
│ ✓ image_url = https://...           │
│ ✓ transfermarkt_id = 148455         │
│                                      │
│ 🔒 name_tr PROTECTED from updates   │
└──────────────────────────────────────┘
```

## Field Update Rules

```
┌────────────────────────────────────────────────────────────────┐
│                     FIELD UPDATE MATRIX                        │
├───────────────────┬──────────────┬────────────┬───────────────┤
│ Field             │ Sportmonks   │ TransferMkt│ Manual        │
├───────────────────┼──────────────┼────────────┼───────────────┤
│ api_id            │ ✓ CREATE     │ ✗ NEVER    │ ✗ NEVER       │
│ team              │ ✓ UPDATE     │ ✗ NEVER    │ ✓ UPDATE      │
│ league            │ ✓ UPDATE     │ ✗ NEVER    │ ✓ UPDATE      │
│ name              │ ✓ CREATE     │ ✓ IF EMPTY │ ✓ UPDATE      │
│ name_tr           │ ✗ NEVER      │ ✗ NEVER    │ ✓ ONLY MANUAL │
│ position          │ ✓ UPDATE     │ ✓ IF EMPTY │ ✓ UPDATE      │
│ height            │ ✓ IF EMPTY   │ ✓ ALWAYS   │ ✓ UPDATE      │
│ weight            │ ✓ IF EMPTY   │ ✓ ALWAYS   │ ✓ UPDATE      │
│ age               │ ✓ UPDATE     │ ✓ ALWAYS   │ ✓ UPDATE      │
│ foot              │ ✗ N/A        │ ✓ ALWAYS   │ ✓ UPDATE      │
│ market_value      │ ✗ N/A        │ ✓ ALWAYS   │ ✓ UPDATE      │
│ transfermarkt_id  │ ✗ N/A        │ ✓ ALWAYS   │ ✓ UPDATE      │
│ image_path        │ ✓ UPDATE     │ ✗ NO       │ ✓ UPDATE      │
│ image_url         │ ✗ N/A        │ ✓ ALWAYS   │ ✓ UPDATE      │
│ contract_expires  │ ✗ N/A        │ ✓ ALWAYS   │ ✓ UPDATE      │
│ player_agent_name │ ✗ N/A        │ ✓ ALWAYS   │ ✓ UPDATE      │
└───────────────────┴──────────────┴────────────┴───────────────┘

Legend:
✓ ALWAYS   = Always update when new data available
✓ CREATE   = Set only when creating player
✓ IF EMPTY = Update only if field is currently empty
✓ UPDATE   = Can be updated anytime
✗ NEVER    = Never automatically updated
✗ N/A      = Not available from this source
```

## Matching Algorithm Flow

```
Player: "Mohamed Salah" (Team: Liverpool FC)
TransferMarket Data: "Mohamed Salah" (Club: Liverpool FC)

┌──────────────────────────────────────┐
│ STEP 1: Check TransferMarkt ID      │
│ player.transfermarkt_id exists?     │
└────┬─────────────────────┬───────────┘
     │ YES                 │ NO
     ▼                     ▼
┌─────────────┐   ┌────────────────────────┐
│ Direct Match│   │ STEP 2: Name + Team    │
│ 100% Sure   │   │ Match                  │
└─────────────┘   └────────┬───────────────┘
                           │
                ┌──────────┴──────────┐
                │ Calculate Similarity │
                │                      │
                │ Name: "Mohamed Salah" vs "Mohamed Salah" = 100%│
                │ Team: "Liverpool FC" vs "Liverpool FC" = 100%  │
                │                      │
                │ Combined Score:      │
                │ (100% × 0.7) + (100% × 0.3) = 100%           │
                └──────────┬───────────┘
                           │
                ┌──────────┴──────────┐
                │ Score >= 80%?       │
                └──────────┬───────────┘
                     YES   │   NO
                     ▼     │   ▼
            ┌─────────┐    │   ┌──────────────┐
            │ MATCH!  │    │   │ Try Name Only│
            │ Update  │    │   │ (85% needed) │
            └─────────┘    │   └──────┬───────┘
                          │          │
                          │     YES  │  NO
                          │     ▼    │  ▼
                          │  ┌─────┐ │ ┌────────┐
                          │  │MATCH│ │ │NO MATCH│
                          │  └─────┘ │ └────────┘
                          └──────────┘
```

## UI Workflow

```
┌──────────────────────────────────────────────────────────┐
│                   Admin Panel                            │
│  ┌────────────────────────────────────────────────┐     │
│  │  Players List                                   │     │
│  │  ┌──────┬─────────────┬──────────┬──────────┐ │     │
│  │  │ Name │ Team        │ Position │ Status   │ │     │
│  │  ├──────┼─────────────┼──────────┼──────────┤ │     │
│  │  │ Salah│ Liverpool   │ Forward  │ Active   │ │     │
│  │  │ Kane │ Bayern      │ Forward  │ Active   │ │     │
│  │  └──────┴─────────────┴──────────┴──────────┘ │     │
│  │                                                 │     │
│  │  [Add Player]  [Fetch Players]  [Update from  │     │
│  │                 (Sportmonks)     TransferMkt] │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                             │
                             │ Click "Update from TransferMarket"
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  Update Modal                            │
│  ┌────────────────────────────────────────────────┐     │
│  │  Update Players from TransferMarket            │     │
│  │  ─────────────────────────────────────────     │     │
│  │                                                 │     │
│  │  Select Sport: [Football ▼]                   │     │
│  │                                                 │     │
│  │  ℹ️ What will be updated?                      │     │
│  │  • Player names and images                     │     │
│  │  • Market values and contracts                 │     │
│  │  • Physical attributes                         │     │
│  │  • Position and foot preference                │     │
│  │                                                 │     │
│  │  ⚠️ name_tr will NOT be updated               │     │
│  │                                                 │     │
│  │  [Close]        [Update from TransferMarket]  │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                             │
                             │ Click "Update"
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  Progress View                           │
│  ┌────────────────────────────────────────────────┐     │
│  │  Matching players with TransferMarket data...  │     │
│  │                                                 │     │
│  │  ████████████████░░░░░░░░░░ 65%              │     │
│  │                                                 │     │
│  │  Updating player information...                │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                             │
                             │ Complete
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  Success Message                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  ✓ Update completed!                           │     │
│  │                                                 │     │
│  │  Details:                                       │     │
│  │  ✓ Total Players: 150                          │     │
│  │  ✓ Successfully Updated: 142                   │     │
│  │  ✓ Matched with TransferMarket: 142            │     │
│  │  ⚠️ Failed to Match: 8                         │     │
│  │                                                 │     │
│  │  Page will reload in 3 seconds...             │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

## Quick Reference

### When to Use Each Button

```
┌─────────────────────────────────────────────────────────────┐
│ Button: "Fetch Players From API"                           │
│ ───────────────────────────────────────────────────────     │
│ Use When: First time importing players from Sportmonks     │
│ Updates:  Creates new players with basic info              │
│ Source:   Sportmonks API                                    │
│ Time:     ~5-10 minutes for 1000 players                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Button: "Update Players From Transfermarket"               │
│ ───────────────────────────────────────────────────────     │
│ Use When: After players exist, to enhance with market data │
│ Updates:  Images, market values, physical stats, contracts │
│ Source:   TransferMarket (your scraping system)            │
│ Time:     ~2-5 minutes for 1000 players                    │
│ Safe:     Does NOT overwrite Sportmonks data or name_tr    │
└─────────────────────────────────────────────────────────────┘
```

### Recommended Workflow

```
Week 1: Initial Setup
═══════════════════════
1. ✅ Run migration
2. ✅ Configure TransferMarket data source
3. ✅ Click "Fetch Players From API" (Sportmonks)
4. ✅ Click "Update Players From Transfermarket"
5. ✅ Manually add name_tr for important players

Weekly Maintenance:
══════════════════
1. 🔄 Run TransferMarket scraping
2. 🔄 Click "Update Players From Transfermarket"
3. 📊 Review statistics

Monthly Tasks:
═════════════
1. 🔄 Click "Fetch Players From API" (for new players)
2. 🔄 Update TransferMarket data
3. ✏️ Update name_tr for new players
4. 🧹 Clean up duplicate/inactive players
```

