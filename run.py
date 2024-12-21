import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import tkinter as tk
from src.app import HospitalManagementSystem

def main():
    root = tk.Tk()
    app = HospitalManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# References
# 1. **Tkinter**
#    - Python's standard GUI library
#    - Used for: Main application interface
#    - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
# 2. **Pathlib**
#    - Used for: Path manipulations
#    - Documentation: [Pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
