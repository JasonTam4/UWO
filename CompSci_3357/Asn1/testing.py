import os

file_path = os.path.join(os.path.dirname(__file__), 'assets', 'index.html')
print(f"File path: {file_path}")

if os.path.exists(file_path):
    print(1)
else:
    print(0)