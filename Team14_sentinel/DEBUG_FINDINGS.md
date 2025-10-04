# Event Detection Debug Summary

## Issues Found and Solutions

### ❌ E001: Scanner Avoidance - NOT DETECTING
**Root Cause:** 
- RFID data has `location` values: `None` and `'IN_SCAN_AREA'`
- Algorithm is looking for `location == 'Checkout'`
- No RFID records match this condition

**Solution Options:**
1. Change algorithm to look for `location == 'IN_SCAN_AREA'` instead of `'Checkout'`
2. Or remove location filter entirely
3. Check if this event type is actually testable with current data

**Recommended Fix:** Update line in `event_detector.py`:
```python
# Change from:
for _, rfid_item in rfid_df[rfid_df['location'] == 'Checkout'].iterrows():

# Change to:
for _, rfid_item in rfid_df[rfid_df['location'] == 'IN_SCAN_AREA'].iterrows():
```

---

### ❌ E004: System Crashes - NOT DETECTING
**Root Cause:**
- Queue monitoring has `status` values: `'Active'`, `'Read Error'`, `'System Crash'`
- Algorithm needs to be checked (not visible in issue)
- Possible case-sensitivity issue or logic problem

**Solution:**
Check the `detect_system_crashes` function logic. The status values exist in the data.

**Data Evidence:**
- Status values in data: `['Active', 'Read Error', 'System Crash']`
- System crash events ARE present in the data

---

### ❌ E006: Long Wait Time - NOT DETECTING  
**Root Cause:**
- Algorithm threshold: 300 seconds (5 minutes)
- Actual max dwell time in data: 290.6 seconds
- Threshold is too high!

**Solution:** Lower the threshold

**Recommended Fix:** Update `event_detector.py`:
```python
# Change from:
def detect_long_wait_time(queue_data, threshold_seconds=300):

# Change to:
def detect_long_wait_time(queue_data, threshold_seconds=250):
# Or even 200 to catch more events
```

**Data Evidence:**
- Max average_dwell_time: 290.6 seconds
- Many records with dwell time > 100 seconds
- Current threshold (300) is higher than any value in dataset

---

## Current Detection Status

| Event ID | Status | Count | Issue |
|----------|--------|-------|-------|
| E001 | ❌ | 0 | Wrong location filter value |
| E002 | ✅ | 23 | Working |
| E003 | ✅ | 10 | Working |
| E004 | ❌ | 0 | Need to check logic |
| E005 | ✅ | 117 | Working |
| E006 | ❌ | 0 | Threshold too high |
| E007 | ✅ | 43 | Working |

**Total Events: 193** (Should be higher with fixes)

---

## Action Items

### Priority 1: Fix E006 (Easy Fix)
Change threshold from 300 to 250 or 200 seconds

### Priority 2: Fix E001 (Easy Fix)  
Change location filter from 'Checkout' to 'IN_SCAN_AREA'

### Priority 3: Debug E004 (Needs Investigation)
Check the system crash detection logic - data exists but not being detected

### Priority 4: Test After Fixes
Run diagnostic again and regenerate events.jsonl

---

## Note on Other Event Types

Based on reference data, these event types also exist but are NOT implemented:
- E000: Success Operation
- E008: Staffing Needs  
- E009: Checkout Station Action

**Question:** Are these required or optional? They may be:
1. Not in scope for the challenge
2. Bonus events
3. Reference examples only

Check project requirements to confirm if these need to be implemented.

---

Generated: October 4, 2025
