# DataProject PDF Column Mapping Reference

Based on the actual PDF images provided:

## Hoag Nicholas (#4, Kuwait SC) - Actual Values from PDF

| Column | Value from PDF | What it represents |
|--------|----------------|-------------------|
| Set indicators | 4, 4, 4 | Played in sets 1, 2, 3 |
| Vote | 6.3 | Player rating |
| **Tot** (Points) | **16** | Total points ✓ |
| BP | 4 | Break points |
| W-L | +10 | Win-Loss differential |
| **Serve Tot** | **16** | Total serves ✓ |
| **Serve Err** | **4** | Service errors ✓ |
| **Serve Pts** | **1** | Service points/aces ✓ |
| **Reception Tot** | **11** | Total receptions ✓ |
| **Reception Err** | **1** | Reception errors ✓ |
| Reception Pos% | 55% | Reception positive % (SKIP) |
| Reception Exc% | 36% | Reception excellent % (SKIP) |
| **Attack Tot** | **25** | Total attacks ✓ |
| **Attack Err** | **1** | Attack errors ✓ |
| Attack Blo | . | Attacks blocked (SKIP) |
| **Attack Pts** | **15** | Attack points ✓ |
| Attack Pts% | 60% | Attack points % (SKIP) |
| **BK Pts** | . | Block points (0) |

## Almisry Hussain (#1, Al Sahel) - Actual Values from PDF

| Column | Value from PDF |
|--------|----------------|
| Set indicators | 6, 5, 6 |
| Vote | 5.5 |
| **Tot** (Points) | **7** |
| BP | 3 |
| W-L | +1 |
| **Serve Tot** | **8** |
| **Serve Err** | **1** |
| **Serve Pts** | **2** |
| **Reception Tot** | **13** |
| **Reception Err** | **1** |
| Reception Pos% | 54% (SKIP) |
| Reception Exc% | 23% (SKIP) |
| **Attack Tot** | **17** |
| **Attack Err** | . |
| Attack Blo | 4 |
| **Attack Pts** | **5** |
| Attack Pts% | 29% (SKIP) |
| **BK Pts** | . |

## Key Points

1. **Skip percentages** - Values like 55, 36, 60, 54, 23, 29 are percentages, NOT counts
2. **Dots (.) = 0** - Missing values should be 0
3. **Reception Excellent** - This is NOT in the visible columns, might be calculated from %
4. **Serve Ace vs Serve Pts** - The "Pts" column under Serve is what we're calling "serve_ace"
5. **Block Pts** - Last column, often empty (.)

## Correct Sequence After Skipping Vote

1. Points Total (16, 7, etc.)
2. BP (skip)
3. W-L (skip)
4. Serve Total
5. Serve Errors  
6. Serve Points
7. Reception Total
8. Reception Errors
9. Reception Pos% (SKIP - it's 55%, 54%, etc.)
10. Reception Exc% (SKIP - it's 36%, 23%, etc.)
11. Attack Total
12. Attack Errors
13. Attack Blocked (skip or use as 0)
14. Attack Points
15. Attack Pts% (SKIP - it's 60%, 29%, etc.)
16. Block Points
