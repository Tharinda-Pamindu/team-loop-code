"""
Diagnostic script to check why certain events are not being detected.
This helps debug the event detection algorithms.
"""

import os
import sys
import json
import pandas as pd

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, src_dir)

from data_loader import load_csv_data
import event_detector

# Data directory - go up to project root, then to data folder
DATA_DIR = os.path.join(script_dir, '..', '..', '..', 'data', 'input')

def load_streaming_data(data_dir):
    """Loads all JSONL streaming data."""
    streams = {}
    for filename in os.listdir(data_dir):
        if filename.endswith('.jsonl'):
            stream_name = filename.replace('.jsonl', '')
            streams[stream_name] = []
            with open(os.path.join(data_dir, filename), 'r') as f:
                for line in f:
                    streams[stream_name].append(json.loads(line))
    return streams

def diagnose_event_detection():
    """Run diagnostics on event detection."""
    print("=" * 80)
    print("PROJECT SENTINEL - EVENT DETECTION DIAGNOSTICS")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading data...")
    products_df, customers_df = load_csv_data(DATA_DIR)
    streaming_data = load_streaming_data(DATA_DIR)
    
    print(f"   ✓ Products: {len(products_df)} rows")
    print(f"   ✓ Customers: {len(customers_df)} rows")
    print(f"   ✓ Streaming datasets loaded:")
    for name, data in streaming_data.items():
        print(f"      - {name}: {len(data)} records")
    
    # Test each detector
    print("\n2. Running event detectors...")
    print("-" * 80)
    
    detectors = [
        ("E001", "Scanner Avoidance", lambda: event_detector.detect_scanner_avoidance(
            streaming_data.get('pos_transactions'), 
            streaming_data.get('rfid_readings')
        )),
        ("E002", "Barcode Switching", lambda: event_detector.detect_barcode_switching(
            streaming_data.get('product_recognition'), 
            streaming_data.get('pos_transactions')
        )),
        ("E003", "Weight Discrepancies", lambda: event_detector.detect_weight_discrepancies(
            streaming_data.get('pos_transactions'), 
            products_df
        )),
        ("E004", "System Crashes", lambda: event_detector.detect_system_crashes(
            streaming_data.get('queue_monitoring')
        )),
        ("E005", "Long Queue Length", lambda: event_detector.detect_long_queue_length(
            streaming_data.get('queue_monitoring')
        )),
        ("E006", "Long Wait Time", lambda: event_detector.detect_long_wait_time(
            streaming_data.get('queue_monitoring')
        )),
        ("E007", "Inventory Discrepancy", lambda: event_detector.detect_inventory_discrepancy(
            streaming_data.get('inventory_snapshots'), 
            streaming_data.get('pos_transactions')
        )),
    ]
    
    results = {}
    for event_id, event_name, detector_func in detectors:
        print(f"\n{event_id}: {event_name}")
        try:
            events = detector_func()
            count = len(events)
            results[event_id] = count
            
            if count > 0:
                print(f"   ✓ SUCCESS: {count} events detected")
                # Show first event as sample
                print(f"   Sample: {json.dumps(events[0], indent=2)}")
            else:
                print(f"   ⚠ WARNING: No events detected")
                
        except Exception as e:
            print(f"   ✗ ERROR: {str(e)}")
            results[event_id] = 0
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_detected = sum(results.values())
    working_detectors = sum(1 for count in results.values() if count > 0)
    
    print(f"\nDetectors working: {working_detectors}/{len(detectors)}")
    print(f"Total events detected: {total_detected}")
    print("\nEvent Type Breakdown:")
    for event_id, count in results.items():
        status = "✓" if count > 0 else "✗"
        print(f"   {status} {event_id}: {count} events")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if results.get('E001', 0) == 0:
        print("\n⚠ E001 (Scanner Avoidance):")
        print("   - Check if RFID readings have location='Checkout'")
        print("   - Verify time_window_seconds is appropriate (default: 10)")
        print("   - Check if SKUs match between RFID and POS data")
        
    if results.get('E004', 0) == 0:
        print("\n⚠ E004 (System Crashes):")
        print("   - Check if queue_monitoring has status != 'active'")
        print("   - Verify offline_duration threshold (default: 60 seconds)")
        
    if results.get('E006', 0) == 0:
        print("\n⚠ E006 (Long Wait Time):")
        print("   - Current threshold: 300 seconds (5 minutes)")
        print("   - Consider lowering threshold if data has shorter wait times")
        print("   - Check queue_monitoring data for average_dwell_time values")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    diagnose_event_detection()
