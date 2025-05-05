import numpy as np

def display_npz_info(file_path):
    # Load the .npz file
    data = np.load(file_path)
    
    # Display the keys (variable names) in the file
    print(f"Keys in the file: {list(data.keys())}")
    
    # Display the data for each key
    for key in data:
        print(f"\nKey: {key}")
        print(f"Data for {key}: \n{data[key]}")

def run():
    # Define the path to your .npz file
    file_path = 'stereo_calibration.npz'
    
    # Call the display function
    display_npz_info(file_path)

def main():
    # Call the run function
    run()

# Call the main function to start the process
if __name__ == "__main__":
    main()
