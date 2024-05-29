import os
import yaml
from random import randrange
import shutil



def count_jpg_images(folder_path, format=".jpg"):
    # Initialize counters for jpg and txt files
    jpg_count = 0
    txt_count = 0

    # Check the format parameter to determine which files to count
    if format == ".jpg":
        # Loop through all files in the specified folder
        for file_name in os.listdir(folder_path):
            # Check if the file name ends with '.jpg'
            if file_name.endswith('.jpg'):
                # Increment the jpg file count
                jpg_count += 1
        # Return the count of jpg files
        return jpg_count
    elif format == ".txt":
        # Loop through all files in the specified folder
        for file_name in os.listdir(folder_path):
            # Check if the file name ends with '.txt'
            if file_name.endswith('.txt'):
                # Increment the txt file count
                txt_count += 1
        # Return the count of txt files
        return txt_count




def get_jpg_image_names(folder_path, format=".jpg"):
    # Check if the format is ".jpg"
    if format == ".jpg":
        # List comprehension to find all files ending with '.jpg' in the specified folder
        jpg_images = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.jpg')]
        # Return the list of jpg file names
        return jpg_images
    else:
        # List comprehension to find all files ending with '.txt' in the specified folder
        txt_images = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.txt')]
        # Return the list of txt file names
        return txt_images



def copy_image(src_folder, dest_folder, image_name):
    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    # Define the full file paths
    src_path = os.path.join(src_folder, image_name)
    dest_path = os.path.join(dest_folder, image_name)

    # Copy the image
    shutil.copy(src_path, dest_path)
    #print(f'Copied {image_name} to {dest_folder}')



def copy_file(src_folder, dest_folder, file_name):
    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    # Define the full file paths
    src_path = os.path.join(src_folder, file_name)
    dest_path = os.path.join(dest_folder, file_name)

    # Copy the file
    shutil.copy(src_path, dest_path)
    #print(f'Copied {file_name} to {dest_folder}')



def split_data():
    # Define directories for dataset, training images, validation images, training labels, and validation labels
    dataset_dir = 'dataset'
    image_train_dir = 'images/train'
    image_val_dir = 'images/val'
    labels_train_dir = 'labels/train'
    labels_val_dir = 'labels/val'

    # Count the number of jpg images in the dataset directory
    number_of_images = count_jpg_images(dataset_dir)

    # Get the list of jpg image names in the dataset directory
    image_names = get_jpg_image_names(dataset_dir)
    # Dictionary to store image names and their corresponding random index
    image_names_index = {}

    # Get the list of txt label names in the dataset directory
    label_names = get_jpg_image_names(dataset_dir, ".txt")
    # Dictionary to store label names and their corresponding random index
    label_names_index = {}

    # Lists to store the names of the labels for training and validation sets
    labels_names_train = []
    labels_names_val = []

    # Add image and label names into the dictionaries with random index values
    for i in range(len(image_names)):
        image_names_index[image_names[i]] = randrange(10)
        label_names_index[label_names[i]] = image_names_index[image_names[i]]

    # Split images and labels into training and validation sets
    for i in range(number_of_images):
        # If the random index is 9 or 0, consider it for validation set
        if list(image_names_index.values())[i] == 9 or list(image_names_index.values())[i] == 0:
            # Copy image to validation directory
            copy_image(dataset_dir, image_val_dir, list(image_names_index.keys())[i])
            # Copy label to validation directory
            copy_file(dataset_dir, labels_val_dir, list(label_names_index.keys())[i])
            # Add label name to validation list
            labels_names_val.append(list(label_names_index.keys())[i])
        else: 
            # Otherwise, consider it for training set
            # Copy image to training directory
            copy_image(dataset_dir, image_train_dir, list(image_names_index.keys())[i])
            # Copy label to training directory
            copy_file(dataset_dir, labels_train_dir, list(label_names_index.keys())[i])
            # Add label name to training list
            labels_names_train.append(list(label_names_index.keys())[i])

    # Return the lists of validation and training label names
    return labels_names_val, labels_names_train



def update_label_id(label_names, path, product_type_id):
    # Initialize an empty string to store the new label content
    st = ""
    names = {}
    # Loop through each label name in the provided list
    for index in range(len(label_names)):
        # Open the current label file in read mode
        with open(path + "/" + label_names[index], "r") as fileref:
            # Read each line in the file
            for i in fileref:
                # Check if the second element in the line matches the product_type_id
                if product_type_id == int(i.split()[1]): 
                    print(product_type_id)
                    print(int(i.split()[1]))

                    # Update the string with the elements after the second one
                    st_helper1= int(i.split()[2]) - 1
                    st_helper2 = " ".join(i.split()[3:])
                    st = (str(st_helper1) + " " + str(st_helper2))
                    
                    names[st_helper1] = i.split()[0]
                    print(st)
                elif product_type_id != int(i.split()[1]): 
                    st = "" # string should stay empty

        # Open the same file in write mode to update its content
        with open(path + "/" + label_names[index], 'w') as file:
            # Write the updated string to the file
            file.write(st)
    print(names)
    return names    



def update_label_names(label_names, path, product_type_list_names=[]):
    # Initialize an empty string to store the new label content
    st = ""
    names = {}
    
    # save all groups in list
    all_groups = [] # liste mit neuen namen
    for element_name in product_type_list_names:
        all_groups.append(element_name)

    # Create a dictionary that maps each group to an integer, so that we start counting from 0
    newLabel_from0 = {group: index for index, group in enumerate(all_groups)} 
    newGroup_from0 = {index: group for group, index in newLabel_from0.items()}

    # Loop through each label name in the provided list
    for index in range(len(label_names)):
        # Open the current label file in read mode
        with open(path + "/" + label_names[index], "r") as fileref:
            # Read each line in the file
            for i in fileref:
                # Check if the second element in the line matches the product_type_id
                for j in product_type_list_names: # Sink
                    
                    if products[j] == int(i.split()[1]): 
                        
                        newID = newLabel_from0.get(j) 
                        st_helper1 = str(newID)
                        # Update the string with the elements after the third one
                        st_helper2 = " ".join(i.split()[3:])
                        # Update the string with the elements after the third one
                        st = (str(st_helper1) + " " + str(st_helper2))
                        
                        names[newID] = newGroup_from0[newID]
                    else:
                        if not st: # if the string is empty
                            st = "" # string should stay empty


        # Open the same file in write mode to update its content
        with open(path + "/" + label_names[index], 'w') as file:
            # Write the updated string to the file
            file.write(st)
    print(names)
    return names





def create_yolo_training_config(folder_path, product_specific=False, product_type_id=None, product_type_list_names=None):
    # Ensure the path exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create the folder structure
    images_train_dir = os.path.join('images', 'train')
    images_val_dir = os.path.join('images', 'val')
    labels_train_dir = os.path.join('labels', 'train')
    labels_val_dir = os.path.join('labels', 'val')

    os.makedirs(images_train_dir, exist_ok=True)
    os.makedirs(images_val_dir, exist_ok=True)
    os.makedirs(labels_train_dir, exist_ok=True)
    os.makedirs(labels_val_dir, exist_ok=True)

    dataset_dir = os.path.join("", "dataset")
    os.makedirs(dataset_dir, exist_ok=True)

    labels_names_val, labels_names_train = split_data()

    products = {"Toilet":0, "Bathtub":1, "Sink":2}

    if product_specific==True:
        # Update label IDs for validation and training sets
        names = update_label_id(labels_names_val, labels_val_dir, product_type_id) ### list names hinzufügen
        names = update_label_id(labels_names_train, labels_train_dir, product_type_id)
    else:
        # Update label IDs for validation and training sets
        names = update_label_names(labels_names_val, labels_val_dir, product_type_list_names)
        names = update_label_names(labels_names_train, labels_train_dir, product_type_list_names)

    # Create the YAML content
    yaml_content = {
        # 'train': os.path.join(folder_path, 'images', 'train'),
        # 'val': os.path.join(folder_path, 'images', 'val'),
        'images':
        {
            'train': images_train_dir,
            'val': images_val_dir
        },
        'labels':
        {
            'train': labels_train_dir,
            'val': labels_val_dir
        },
        'names': names if names else [],
        'nc': len(names) if names else 0
    }

    if product_specific and product_type_id is not None:
        yaml_content['product_type_id'] = product_type_id

    # Write the YAML file
    parent_folder_path = os.path.dirname(folder_path)
    yaml_path = os.path.join(parent_folder_path, 'data.yaml')

    with open(yaml_path, 'w') as yaml_file:
        yaml.dump(yaml_content, yaml_file, default_flow_style=False)
    print(f'YOLO training configuration created at {yaml_path}')
    print(f'Folder structure created under {folder_path}')





products = {"Toilet":0, "Bathtub":1, "Sink":2}

# Example usage
# create_yolo_training_config("path/to/directory", product_specific=False, product_type_id=products["Bathtub"])

create_yolo_training_config("C:/Users/Liva Ausma/Documents/WORK/DFKI/DVC/AI/training_folder/dataset", product_specific=True, product_type_id=products["Bathtub"])
# create_yolo_training_config("C:/Users/Liva Ausma/Documents/WORK/DFKI/DVC/AI/training_folder/dataset", product_specific=False, product_type_list_names=["Sink", "Toilet"])

