import subprocess

# List of scripts to run
scripts = [
    "1.SQL_Subiekt.py",  # Replace with your actual script names
    "2.Api_Woo.py",
    "3.0.Reports.py",
    "3.1.Auto_Update.py"
]

# Function to run a specific script
def run_script(script):
    try:
        print(f"Running {script}...")
        subprocess.run(["python", script], check=True)
        print(f"{script} completed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")

# Function to run scripts sequentially based on user's choice
def run_scripts_based_on_choice():
    print("Which scripts would you like to run?")
    print("1 SQL_Subiekt.py")
    print("2 Api_Woo.py")
    print("3 Reports.py")
    print("4 Auto_Update.pyy")
    print("5 Run all scripts")

    choice = input("Enter the number (or 5 for all): ").strip()

    if choice == '5':  # Run all scripts
        for script in scripts:
            run_script(script)
    elif choice in ['1', '2', '3', '4']:  # Run specific script
        script_index = int(choice) - 1  # Adjust for 0-based index
        run_script(scripts[script_index])
    else:
        print("Invalid choice. Please try again.")

# Run the function to ask the user and run the scripts
run_scripts_based_on_choice()

