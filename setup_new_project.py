"""
Project Initialization Script

This script automates the creation of a new Python project structure with the following components:
- Main Python file with basic template
- README.md with setup instructions
- requirements.txt for dependencies
- Optional Python virtual environment setup

Usage:
    python new_project.py PROJECT_NAME [--no-venv]

Options:
    PROJECT_NAME    Name of the project (will create a directory with this name)
    --no-venv       Skip virtual environment setup
"""

import os
import sys
import argparse  # For parsing command-line arguments
import subprocess  # For running shell commands
import platform  # For detecting the operating system
from pathlib import Path  # For cross-platform path handling

def create_project_structure(project_name):
    """
    Creates the basic project directory structure and files.
    
    Args:
        project_name (str): Name of the project/directory to create
        
    Returns:
        Path: Path object pointing to the created project directory
    """
    # Create project directory if it doesn't exist
    # Using Path for cross-platform path handling
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)  # exist_ok=True prevents errors if directory exists
    
    # Create main Python file with the same name as the project
    # This follows Python naming conventions for the main module
    main_py = project_dir / f"{project_name}.py"  # Uses pathlib's / operator for joining paths
    if not main_py.exists():
        with open(main_py, 'w') as f:
            f.write(f'''"""{project_name} - A new Python project"""

def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
''')
    
    # Create README.md with basic project documentation
    # This includes setup instructions and usage examples
    readme = project_dir / "README.md"
    if not readme.exists():
        with open(readme, 'w') as f:
            f.write(f"# {project_name}\n\n"
                    "## Description\n"
                    "A new Python project.\n\n"
                    "## Setup\n"
                    "1. Create a virtual environment\n"
                    "   ```powershell\n"
                    f"   cd {project_name}\\n   python -m venv venv\n   .\\venv\\Scripts\\activate\n   pip install -r requirements.txt\n   ```\n"
                    "\n## Usage\n"
                    f"Run `python {project_name}.py`")
    
    # Create requirements.txt for managing Python dependencies
    # This file will be used by pip to install required packages
    requirements = project_dir / "requirements.txt"
    if not requirements.exists():
        with open(requirements, 'w') as f:
            f.write("# Add your project dependencies here\n"
                    "# Example:\n"
                    "# requests==2.31.0\n"
                    "# numpy>=1.21.0\n")
    
    return project_dir

def setup_virtualenv(project_dir):
    """
    Sets up a Python virtual environment in the specified directory.
    
    Args:
        project_dir (Path): Path object pointing to the project directory
    """
    venv_dir = project_dir / "venv"
    if not venv_dir.exists():
        print(f"Creating virtual environment in {venv_dir}...")
        subprocess.run(["python", "-m", "venv", str(venv_dir)], check=True)

        # Determine the correct paths based on the operating system
        # Windows uses Scripts/activate and python.exe
        # Unix-based systems use bin/activate and python
        if platform.system() == "Windows":
            activate_script = venv_dir / "Scripts" / "activate"
            pip_executable = venv_dir / "Scripts" / "python.exe"
        else:
            activate_script = venv_dir / "bin" / "activate"
            pip_executable = venv_dir / "bin" / "python"

        print("Virtual environment created successfully!")
        print(f"\nTo activate the virtual environment, run:")
        print(f"  cd {project_dir}")
        print(f"  .\\venv\\Scripts\\activate")
    else:
        print("Virtual environment already exists.")

def main():
    """
    Main function that parses command-line arguments and coordinates the project setup.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Create a new Python project structure.')
    
    # Required positional argument for project name
    parser.add_argument('project_name', 
                       help='Name of the project (will create a directory with this name)')
    
    # Optional flag to skip virtual environment setup
    parser.add_argument('--no-venv', 
                       action='store_true', 
                       help='Skip virtual environment setup')
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    print(f"Creating new Python project: {args.project_name}")
    
    # Create the basic project structure
    project_dir = create_project_structure(args.project_name)
    
    # Set up virtual environment unless --no-venv flag is used
    if not args.no_venv:
        setup_virtualenv(project_dir)
    
    # Print success message with project location
    print("\nProject structure created successfully!")
    print(f"Location: {os.path.abspath(project_dir)}")
    
    # Provide instructions for the next steps
    if not args.no_venv:
        print("\nTo get started:")
        print(f"1. cd {args.project_name}")
        print("2. .\\venv\\Scripts\\activate  # On Windows")
        print("   # or")
        print("   # source venv/bin/activate  # On Unix/MacOS")
        print("3. pip install -r requirements.txt")

if __name__ == "__main__":
    # This ensures that main() is only called when the script is run directly,
    # not when it's imported as a module
    main()
