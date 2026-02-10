import os
from pathlib import Path

print("Current working directory:", os.getcwd())
print("\n=== Checking File Structure ===")

# Check if static folder exists
static_path = Path("static")
if static_path.exists():
    print("✓ 'static' folder exists")
    
    # Check if index.html exists
    index_path = static_path / "index.html"
    if index_path.exists():
        print("✓ 'static/index.html' exists")
    else:
        print("✗ 'static/index.html' NOT FOUND!")
else:
    print("✗ 'static' folder NOT FOUND!")

print("\n=== Current Directory Contents ===")
for item in Path(".").iterdir():
    print(f"  {item.name}")

print("\n=== Expected Structure ===")
print("Your project should look like:")
print("  C:\\ML\\Posture_Detection\\")
print("  ├── main.py")
print("  ├── small640.pt")
print("  └── static/")
print("      └── index.html")