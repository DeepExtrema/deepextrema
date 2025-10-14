#!/usr/bin/env python3
"""
Test all dashboard components
"""

import os
import sys

def test_imports():
    """Test all required modules can be imported"""
    print("[INFO] Testing imports...")
    modules = ['github', 'requests', 'matplotlib', 'numpy', 'yaml']
    for module in modules:
        try:
            __import__(module if module != 'github' else 'github.Github')
            print(f"  + {module}")
        except ImportError as e:
            print(f"  X {module}: {e}")
            return False
    return True

def test_env_vars():
    """Test required environment variables"""
    print("[INFO] Testing environment variables...")
    required = ['GITHUB_TOKEN', 'GITHUB_REPOSITORY']
    optional = ['OPENAI_API_KEY', 'NASA_API_KEY']
    
    all_required = True
    for var in required:
        if os.getenv(var):
            print(f"  + {var} is set")
        else:
            print(f"  X {var} is MISSING (required)")
            all_required = False
    
    for var in optional:
        if os.getenv(var):
            print(f"  + {var} is set")
        else:
            print(f"  ? {var} is not set (optional)")
    
    return all_required

def test_readme_sections():
    """Test README has all required sections"""
    print("[INFO] Testing README sections...")
    required_sections = [
        'LAUNCH', 'SHIPLOG', 'VELOCITYWAVES', 'DNAHELIX', 'THRUSTERS',
        'MISSIONSUCCESS', 'LIGHTNING', 'NEURAL', 'MODEL', 'COSMICFACT',
        'QUOTE', 'BATTERY', 'TRAJECTORY', 'EVOLUTION', 'RADAR'
    ]
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("  X README.md not found")
        return False
    
    all_found = True
    for section in required_sections:
        if f'<!--START_SECTION:{section}-->' in content and f'<!--END_SECTION:{section}-->' in content:
            print(f"  + {section}")
        else:
            print(f"  X {section} is MISSING")
            all_found = False
    
    return all_found

def test_config_files():
    """Test configuration files exist"""
    print("[INFO] Testing configuration files...")
    
    config_files = [
        ('config.yaml', 'Configuration file'),
        ('requirements.txt', 'Dependencies file'),
        ('scripts/utils.py', 'Utility functions'),
        ('scripts/cache.py', 'Cache system'),
        ('scripts/rate_limit_check.py', 'Rate limit checker')
    ]
    
    all_exist = True
    for file_path, description in config_files:
        if os.path.exists(file_path):
            print(f"  + {file_path} ({description})")
        else:
            print(f"  X {file_path} ({description}) MISSING")
            all_exist = False
    
    return all_exist

def test_data_directories():
    """Test data directories exist"""
    print("[INFO] Testing data directories...")
    
    directories = [
        'data',
        'data/cache',
        'data/logs'
    ]
    
    all_exist = True
    for directory in directories:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"  + {directory}/")
        else:
            print(f"  X {directory}/ MISSING")
            all_exist = False
    
    return all_exist

def test_scripts_executable():
    """Test that all scripts can be imported"""
    print("[INFO] Testing scripts are executable...")
    
    script_files = [
        'battery.py', 'cosmic_fact.py', 'evolution.py', 'quote.py', 'model_week.py',
        'trajectory.py', 'shiplog.py', 'velocity_waves.py', 'dna_helix.py',
        'thrusters.py', 'mission_success.py', 'lightning_commits.py', 'neural_pathways.py',
        'signal_radar.py', 'parallax_stars.py', 'gravity_well.py', 'orbital_mechanics.py'
    ]
    
    all_executable = True
    for script in script_files:
        script_path = f'scripts/{script}'
        if os.path.exists(script_path):
            try:
                # Try to compile the script
                with open(script_path, 'r') as f:
                    compile(f.read(), script_path, 'exec')
                print(f"  + {script}")
            except SyntaxError as e:
                print(f"  X {script}: Syntax error - {e}")
                all_executable = False
            except Exception as e:
                print(f"  X {script}: Error - {e}")
                all_executable = False
        else:
            print(f"  X {script} MISSING")
            all_executable = False
    
    return all_executable

def main():
    """Run all tests"""
    print("Running DeepExtrema Dashboard Tests\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Variables", test_env_vars),
        ("README Sections", test_readme_sections),
        ("Configuration Files", test_config_files),
        ("Data Directories", test_data_directories),
        ("Script Executability", test_scripts_executable)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"Result: {'PASS' if result else 'FAIL'}\n")
        except Exception as e:
            print(f"  X {test_name} failed with exception: {e}")
            results.append((test_name, False))
            print(f"Result: FAIL\n")
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return True
    else:
        print(f"\n[FAILED] {total - passed} test(s) failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
