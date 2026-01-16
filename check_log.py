import os
try:
    size = os.path.getsize('script_run.log')
    print(f"Log size: {size} bytes")

    with open('script_run.log', 'r', encoding='utf-8', errors='ignore') as f:
         print("First 100 chars:")
         print(f.read(100))
except Exception as e:
    print(e)

