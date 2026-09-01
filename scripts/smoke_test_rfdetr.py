import os
from pathlib import Path
from evaluate_detector import RFDETRDetector, IBVAP_CLASSES, RFDETR_CLASS_MAPPING

def smoke_test():
    print("Running Smoke Test for RF-DETR...")
    try:
        from evaluate_detector import RFDETRDetector
        detector = RFDETRDetector('rfdetr-s', 'cpu')
        detector.load()
        print("[PASS] Model loaded successfully.")
    except Exception as e:
        print(f"[FAIL] Could not load model: {e}")
        return
        
    # Check mappings
    assert RFDETR_CLASS_MAPPING[0] == 0 # Person
    assert RFDETR_CLASS_MAPPING[2] == 1 # Car
    print("[PASS] Class mapping verified.")
    
    print("Smoke Test Passed!")

if __name__ == "__main__":
    smoke_test()
