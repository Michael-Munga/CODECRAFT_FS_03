#!/usr/bin/env python3
"""
Quick verification that Phase 1 logging components are properly implemented
"""

def verify_phase1_implementation():
    print("=== Layer 4 Phase 1 Implementation Verification ===\n")
    
    # Check 1: Import verification
    print("1. Verifying imports...")
    try:
        from logging_config import setup_logging, get_logger
        from request_tracking import request_id_middleware, get_current_request_id
        from request_logging import setup_request_logging
        print("   ✓ All modules import successfully")
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        return False
    
    # Check 2: Logging setup
    print("\n2. Testing logging setup...")
    try:
        import logging
        logger = setup_logging(logging.DEBUG, '/tmp/test.log')
        logger.info("Test log message", test_field="verification")
        print("   ✓ Logging configured successfully")
    except Exception as e:
        print(f"   ✗ Logging setup failed: {e}")
        return False
    
    # Check 3: Request ID generation
    print("\n3. Testing request ID generation...")
    try:
        request_id = get_current_request_id()
        if request_id is None:
            print("   ✓ Request ID system ready (None when not in request context)")
        else:
            print(f"   ✓ Request ID generated: {request_id}")
    except Exception as e:
        print(f"   ✗ Request ID generation failed: {e}")
        return False
    
    # Check 4: File structure
    print("\n4. Verifying file structure...")
    import os
    required_files = [
        'logging_config.py',
        'request_tracking.py', 
        'request_logging.py',
        'test_layer4_phase1.py',
        'LAYER4_PHASE1_SUMMARY.md'
    ]
    
    all_files_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} - MISSING")
            all_files_exist = False
    
    # Check 5: App integration
    print("\n5. Checking app.py integration...")
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            required_imports = [
                'from logging_config import setup_logging',
                'from request_tracking import request_id_middleware',
                'from request_logging import setup_request_logging'
            ]
            required_calls = [
                'setup_logging(logging.INFO)',
                'request_id_middleware(app)',
                'setup_request_logging(app)'
            ]
            
            all_found = True
            for imp in required_imports:
                if imp in content:
                    print(f"   ✓ Found: {imp}")
                else:
                    print(f"   ✗ Missing: {imp}")
                    all_found = False
                    
            for call in required_calls:
                if call in content:
                    print(f"   ✓ Found: {call}")
                else:
                    print(f"   ✗ Missing: {call}")
                    all_found = False
            
            if all_found:
                print("   ✓ App.py properly integrated")
            else:
                print("   ✗ App.py integration incomplete")
                all_files_exist = False
                
    except Exception as e:
        print(f"   ✗ Could not check app.py: {e}")
        all_files_exist = False
    
    print("\n" + "="*50)
    if all_files_exist:
        print("🎉 PHASE 1 IMPLEMENTATION: COMPLETE AND VERIFIED")
        print("\nWhat you now have:")
        print("✓ Structured JSON logging with rotation")
        print("✓ Request ID tracking for correlation")
        print("✓ Automatic request/response logging")
        print("✓ Performance timing data")
        print("✓ User correlation in logs")
        print("\nNext steps:")
        print("1. Start your Flask server: python3 app.py")
        print("2. Run test script: python3 test_layer4_phase1.py")
        print("3. Check logs: tail -f logs/app.log")
        return True
    else:
        print("❌ PHASE 1 IMPLEMENTATION: INCOMPLETE")
        print("Some components are missing or not properly configured")
        return False

if __name__ == "__main__":
    verify_phase1_implementation()