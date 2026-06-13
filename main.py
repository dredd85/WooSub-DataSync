import subprocess

# List of scripts to run
scripts = [
    "extract_subiekt.py",
    "fetch_woocommerce.py",
    "report_differences.py",
    "auto_update_inventory.py"
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
    while True:
        print("What would you like to proceed first?")
        print("(1)Extract Subiekt")
        print("(2)Fetch WooCommerce")
        print("(3)Show Reports")
        print("(4)Update Inventory")
        print("(5)Run all scripts")
        print("(q)Quit")

        choice = input("Enter the number (or 5 for all, q to quit): ").strip().lower()

        if choice == '5':  # Run all scripts
            for script in scripts:
                run_script(script)
            break
        elif choice in ['1', '2', '3', '4']:  # Run specific script
            script_index = int(choice) - 1  # Adjust for 0-based index
            run_script(scripts[script_index])
            break
        elif choice == 'q':
            print("Exiting.")
            break
        else:
            print(f"Invalid choice '{choice}'. Please try again.\n")
            import time
            time.sleep(2)

# Run the function to ask the user and run the scripts
run_scripts_based_on_choice()

