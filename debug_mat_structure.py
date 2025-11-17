#!/usr/bin/env python3
"""
Debug script to understand MAT file structure from OpenModelica
"""

from scipy.io import loadmat
from pathlib import Path
import numpy as np

# Find a recent MAT file
workspace = Path("workspaces/GUI_Simulator")
mat_files = list(workspace.glob("*.mat"))

if not mat_files:
    print("No MAT files found")
    exit(1)

mat_file = sorted(mat_files)[-1]  # Get most recent
print(f"Analyzing: {mat_file}\n")

data = loadmat(str(mat_file))

print("=" * 80)
print("MAT FILE STRUCTURE")
print("=" * 80)

for key in sorted(data.keys()):
    value = data[key]
    print(f"\nKey: '{key}'")
    print(f"  Type: {type(value)}")
    print(f"  Shape: {value.shape}")
    print(f"  DType: {value.dtype}")
    
    if key == 'name':
        print(f"  Content (variable names):")
        if value.dtype.kind == 'O':  # Object array
            for i, name_array in enumerate(value):
                try:
                    name_str = ''.join(chr(c) for c in name_array if 32 <= c < 127)
                    print(f"    [{i}] {name_str}")
                except:
                    print(f"    [{i}] <parse error>")
    
    elif key == 'dataInfo':
        print(f"  Data info shape: {value.shape}")
        print(f"  First few entries: {value.flatten()[:20]}")
    
    elif key in ['data_1', 'data_2']:
        if len(value) <= 10:
            print(f"  Values: {value.flatten()}")
        else:
            print(f"  First 5: {value.flatten()[:5]}")
            print(f"  Last 5: {value.flatten()[-5:]}")
            print(f"  Min: {value.min()}, Max: {value.max()}")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

# Proper interpretation
if 'data_1' in data and 'data_2' in data:
    time = data['data_1'].flatten()
    var_data = data['data_2']
    
    print(f"\nTime array: {len(time)} points")
    print(f"Variable data shape: {var_data.shape}")
    
    if 'name' in data:
        names = data['name']
        print(f"\nVariable names ({len(names)} total):")
        
        for i, name_array in enumerate(names):
            try:
                # Handle both string arrays and byte arrays
                if isinstance(name_array, np.ndarray):
                    if name_array.dtype.kind in ['U', 'S']:  # Unicode or byte string
                        name_str = str(name_array)
                    else:
                        name_str = ''.join(chr(int(c)) for c in name_array if 32 <= int(c) < 127)
                else:
                    name_str = str(name_array)
                
                print(f"  Variable {i}: {name_str}")
            except Exception as e:
                print(f"  Variable {i}: <error parsing: {e}>")
    
    # Show dataInfo structure
    if 'dataInfo' in data:
        info = data['dataInfo']
        print(f"\nData info explains variable storage:")
        print(f"  Shape: {info.shape}")
        print(f"  Content:\n{info}")
