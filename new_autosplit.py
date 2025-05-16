import os
import random
import shutil
import pydicom
from time import time

def get_folders(path):
    """
    Retrieve all subfolders in a given directory that contain '.dcm' files.
    """
    folders = []
    for root, dirs, files in os.walk(path):
        if any(file.endswith('.dcm') for file in files):
            folders.append(root)
    return folders

def process_batch(batch_folders):
    """
    Process a batch of folders to group DICOM files by their 'AcquisitionTime'.
    Create new folders within the original folder named "<AcquisitionTime>_binX".
    """
    for folder in batch_folders:
        acquisition_dict = {}
        
        # Collect all DICOM files and group them by 'AcquisitionTime'
        all_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.dcm')]
        for file_path in all_files:
            try:
                dataset = pydicom.dcmread(file_path, stop_before_pixels=True)
                acquisition_time = getattr(dataset, 'SeriesTime', 'Unknown')
                
                if acquisition_time not in acquisition_dict:
                    acquisition_dict[acquisition_time] = []
                acquisition_dict[acquisition_time].append(file_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        # Sort 'AcquisitionTime' and process files
        for idx, (acquisition_time, files) in enumerate(sorted(acquisition_dict.items()), start=1):
            new_folder_name = f"{acquisition_time}_bin{idx}"
            new_folder_path = os.path.join(folder, new_folder_name)
            
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            
            # Move files to the new folder
            for file_path in files:
                shutil.move(file_path, os.path.join(new_folder_path, os.path.basename(file_path)))
            print(f"Moved {len(files)} files to {new_folder_path}")

def process_in_batches(root_path, batch_size=10):
    """
    Randomly process directories in batches until all have been processed.
    """
    all_folders = get_folders(root_path)
    random.shuffle(all_folders)

    # Process folders in batches
    for i in range(0, len(all_folders), batch_size):
        batch_folders = all_folders[i:i + batch_size]
        print(f"Processing batch from {i + 1} to {min(i + batch_size, len(all_folders))} of {len(all_folders)}...")
        process_batch(batch_folders)

# Example usage
if __name__ == "__main__":
    start_time = time()
    process_in_batches(r'C:\Users\Mirai\Desktop\LYG\HBV_ECT')
    end_time = time()
    print(f"Total processing time: {end_time - start_time} seconds")