import os
import yaml
from random import randrange
import shutil
from collections import OrderedDict

# Create the path for the 'dataset' directory
dataset_dir = os.path.join("", "dataset")
# Create the 'dataset' directory if it doesn't exist
os.makedirs(dataset_dir, exist_ok=True)
# Print the list of files and directories in the 'dataset' directory
print(os.listdir(dataset_dir))

# Create the path for the 'updatedDataset' directory
updated_dataset_dir = os.path.join("", "updatedDataset")
# Create the 'updatedDataset' directory if it doesn't exist
os.makedirs(updated_dataset_dir, exist_ok=True)
# Print the list of files and directories in the 'updatedDataset' directory
print(os.listdir(updated_dataset_dir))

# 440 format dimensions for height and width
H = 440.0
B = 440.0

#Part1: Normalizing the labels 
def get_label_names(folder_path, format=".txt"):
    """
    Gets the names of files with the specified format in the given folder.

    Args:
    folder_path (str): The path to the folder where the files are located.
    format (str): The file format to look for (default is ".txt").

    Returns:
    list: A list of file names with the specified format.
    """
    # Check if the format is ".txt"
    if format == ".txt":
        # List comprehension to find all files ending with '.txt' in the specified folder
        txt_labels = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.txt')]
        # Return the list of txt file names
        return txt_labels

def check_update_outliers(updated_x, updated_y, side_size_x, side_size_y):
    """
    Adjusts the bounding box coordinates and sizes to ensure they fit within the boundary [0, 1].

    Args:
    updated_x (float): The normalized x-coordinate of the center of the bounding box.
    updated_y (float): The normalized y-coordinate of the center of the bounding box.
    side_size_x (float): The normalized width of the bounding box.
    side_size_y (float): The normalized height of the bounding box.

    Returns:
    tuple: The potentially adjusted coordinates and sizes.
    """
    # Check for the corners where both X and Y boundaries are exceeded
    # Bottom-left corner
    if (updated_x - side_size_x / 2 < 0) and (updated_y - side_size_y / 2 < 0):
        # Adjust both x and y coordinates to bring the bounding box within the boundary
        updated_x = side_size_x / 2
        updated_y = side_size_y / 2

    # Bottom-right corner
    if (updated_x + side_size_x / 2 > 1) and (updated_y - side_size_y / 2 < 0):
        # Adjust both x and y coordinates to bring the bounding box within the boundary
        updated_x = 1 - side_size_x / 2
        updated_y = side_size_y / 2

    # Top-left corner
    if (updated_x - side_size_x / 2 < 0) and (updated_y + side_size_y / 2 > 1):
        # Adjust both x and y coordinates to bring the bounding box within the boundary
        updated_x = side_size_x / 2
        updated_y = 1 - side_size_y / 2

    # Top-right corner
    if (updated_x + side_size_x / 2 > 1) and (updated_y + side_size_y / 2 > 1):
        # Adjust both x and y coordinates to bring the bounding box within the boundary
        updated_x = 1 - side_size_x / 2
        updated_y = 1 - side_size_y / 2

    # Check if the right edge of the bounding box exceeds the right boundary (1.0)
    if updated_x + side_size_x / 2 > 1:
        # Adjust the x coordinate to bring the bounding box within the boundary
        updated_x = updated_x - (updated_x + side_size_x / 2 - 1) / 2
        # Adjust the width of the bounding box to fit within the boundary
        side_size_x = 2 * (1 - updated_x)
    # Check if the left edge of the bounding box exceeds the left boundary (0.0)
    elif updated_x - side_size_x / 2 < 0:
        # Adjust the x coordinate to bring the bounding box within the boundary
        updated_x = updated_x + (side_size_x / 2 - updated_x) / 2
        # Adjust the width of the bounding box to fit within the boundary
        side_size_x = 2 * updated_x

    # Check if the top edge of the bounding box exceeds the top boundary (1.0)
    if updated_y + side_size_y / 2 > 1:
        # Adjust the y coordinate to bring the bounding box within the boundary
        updated_y = updated_y - (updated_y + side_size_y / 2 - 1) / 2
        # Adjust the height of the bounding box to fit within the boundary
        side_size_y = 2 * (1 - updated_y)
    # Check if the bottom edge of the bounding box exceeds the bottom boundary (0.0)
    elif updated_y - side_size_y / 2 < 0:
        # Adjust the y coordinate to bring the bounding box within the boundary
        updated_y = updated_y + (side_size_y / 2 - updated_y) / 2
        # Adjust the height of the bounding box to fit within the boundary
        side_size_y = 2 * updated_y

    # Return the potentially adjusted coordinates and sizes
    return updated_x, updated_y, side_size_x, side_size_y

def update_normalize_xy(param, side_size, dimension="X", H=440., B=440.):
    """
    Normalizes the param value for the specified dimension (X or Y).

    Args:
    param (float): The parameter value to normalize.
    side_size (float): The size to be added for centering.
    dimension (str): The dimension to normalize ('X' or 'Y').
    H (float): The maximum range for X dimension (default is 3840.0).
    B (float): The maximum range for Y dimension (default is 2160.0).

    Returns:
    float: The normalized parameter value in the range [0, 1].

    Raises:
    ValueError: If the dimension is not 'X' or 'Y'.
    """
    if dimension == "X":
        # Normalize the param value for the X dimension
        return (param + side_size / 2) / H
    elif dimension == "Y":
        # Normalize the param value for the Y dimension
        return (param + side_size / 2) / B
    else:
        raise ValueError("Dimension must be 'X' or 'Y'")

def change_label_content(path, updated_path):
    """
    Updates the label content with normalized coordinates and side sizes.

    Args:
    path (str): The file path of the original label file.
    updated_path (str): The file path to save the updated label file.
    """
    # Initialize variables to hold label index, coordinates, and sizes
    index = 0
    updated_x = 0
    updated_y = 0
    side_size_x = 0
    side_size_y = 0

    sts = []

    # Open the file at the given path in read mode
    with open(path, "r") as fileref:
        # Iterate over each line in the file
        for i in fileref:
            # Split the line into parts and parse the values as floats
            name = i.split(" ")[0]
            index1 = (i.split(" ")[1])
            index2 = (i.split(" ")[2])
            updated_x = float(i.split(" ")[3])
            updated_y = float(i.split(" ")[4])
            side_size_x = float(i.split(" ")[5])
            side_size_y = float(i.split(" ")[6])

            # Normalize the x and y coordinates
            updated_x = update_normalize_xy(updated_x, side_size_x, "X")
            updated_y = update_normalize_xy(updated_y, side_size_y, "Y")

            # Normalize the side sizes (assuming H and B are global or defined elsewhere)
            side_size_x = side_size_x / H
            side_size_y = side_size_y / B

            updated_x, updated_y, side_size_x, side_size_y = check_update_outliers(updated_x, updated_y, side_size_x, side_size_y)

            # Create a string with updated values concatenated
            st = f"{name} {index1} {index2} {updated_x} {updated_y} {side_size_x} {side_size_y}"
            sts.append(st)

    # Open the file at the given path in write mode and write the updated string
    with open(updated_path, "w") as file:
      print(sts)
      file.writelines("\n".join(sts))


#Part2: Postprocessing the labels 
def count_jpg_images(folder_path, format=".jpg"):
    """
    Counts the number of files with the specified format in the given folder.

    Args:
    folder_path (str): The path to the folder where the files are located.
    format (str): The file format to count (default is ".jpg").

    Returns:
    int: The count of files with the specified format.
    """
    
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
    """
    Gets the names of files with the specified format in the given folder.

    Args:
    folder_path (str): The path to the folder where the files are located.
    format (str): The file format to look for (default is ".jpg").

    Returns:
    list: A list of file names with the specified format.
    """
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
    
    """
    Copies an image from the source folder to the destination folder.

    Args:
    src_folder (str): The path to the source folder where the image is located.
    dest_folder (str): The path to the destination folder where the image will be copied.
    image_name (str): The name of the image file to copy.
    """
    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    # Define the full file paths
    src_path = os.path.join(src_folder, image_name)
    dest_path = os.path.join(dest_folder, image_name)

    # Copy the image
    shutil.copy(src_path, dest_path)

def copy_file(src_folder, dest_folder, file_name):
    """
    Copies a label from the source folder to the destination folder.

    Args:
    src_folder (str): The path to the source folder where the label is located.
    dest_folder (str): The path to the destination folder where the label will be copied.
    file_name (str): The name of the label to copy.

    """
    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    # Define the full file paths
    src_path = os.path.join(src_folder, file_name)
    dest_path = os.path.join(dest_folder, file_name)

    # Copy the file
    shutil.copy(src_path, dest_path)


def copy_all_images(src_folder, dest_folder, image_names):
    """
    Copies all specified images from the source folder to the destination folder.

    Args:
    src_folder (str): The path to the source folder where the images are located.
    dest_folder (str): The path to the destination folder where the images will be copied.
    image_names (list): A list of image file names to copy.
    """
    for image_name in image_names:
         copy_image(src_folder, dest_folder, image_name)


def split_data():
    """
    Splits the dataset into training and validation sets for both images and labels.

    Directories for dataset, training images, validation images, training labels, 
    and validation labels are predefined.

    Returns:
    tuple: Lists of validation and training label names.
    """
    # Define directories for dataset, training images, validation images, training labels, and validation labels
    dataset_dir = 'updatedDataset'
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
    """
    Updates the label IDs in the specified label files based on the given product_type_id.

    Args:
    label_names (list): A list of label file names to be updated.
    path (str): The directory path where the label files are located.
    product_type_id (int): The product type ID to be checked and updated in the label files.

    Returns:
    dict: A dictionary with updated IDs and corresponding original IDs.
    """
    names = {}
    # Loop through each label name in the provided list
    for index in range(len(label_names)):
        # Open the current label file in read mode
        with open(path + "/" + label_names[index], "r") as fileref:
            # Initialize an empty string to store the new label content
            st = ""
            # Read each line in the file
            for i in fileref:
                # Check if the second element in the line matches the product_type_id
                if product_type_id == int(i.split()[1]):

                    # Update the string with the elements after the second one
                    st_helper1= int(i.split()[2]) - 1
                    st_helper2 = " ".join(i.split()[3:])
                    st = (str(st_helper1) + " " + str(st_helper2))

                    names[st_helper1] = i.split()[0]
                else:
                    if not st: # if the string is empty
                        st = "" # string should stay empty

        # Open the same file in write mode to update its content
        with open(path + "/" + label_names[index], 'w') as file:
            # Write the updated string to the file
            file.write(st)
    #print(names)
    return names

def update_label_names(label_names, path, product_type_list_names=[]):
    """
    Updates the label names in the specified label files based on the given product_type_list_names.

    Args:
    label_names (list): A list of label file names to be updated.
    path (str): The directory path where the label files are located.
    product_type_list_names (list): A list of product type names to be checked and updated in the label files.

    Returns:
    dict: A dictionary with updated IDs and corresponding original names.
    """
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
    return names





def create_yolo_training_config(folder_path, product_specific=False, product_type_id=None, product_type_list_names=None):
    """
    Creates a YOLO training configuration file and updates label IDs if necessary.

    Args:
    folder_path (str): The directory path for creating the training configuration.
    product_specific (bool): Flag to determine if the configuration is product-specific.
    product_type_id (int): The product type ID to be checked and updated in the label files.
    product_type_list_names (list): A list of product type names to be checked and updated in the label files.

    """
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

    dataset_dir = os.path.join("", "updatedDataset")
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

    # Define the YAML configuration structure
    yolo_config = OrderedDict([
      ('path', '../updatedDataset'),
      ('train', 'images/train'),
      ('val', 'images/val'),
      ('test', ''),
      ('names', names)
    ])

    # Function to represent OrderedDict as a standard YAML dictionary
    def represent_ordereddict(dumper, data):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

    yaml.add_representer(OrderedDict, represent_ordereddict)


    # Write the configuration to a YAML file
    with open('data.yaml', 'w') as file:
        yaml.dump(yolo_config, file, default_flow_style=False)

    print("YAML configuration file has been generated.")


get_label_names(dataset_dir, format=".txt")
for i in get_label_names(dataset_dir, format=".txt"):
  path = dataset_dir + "/" + i
  path = "dataset" + "/" + i
  updated_path = "updatedDataset" + "/" + i
  change_label_content(path, updated_path)
  #copy images in folder with normalized labels
copy_all_images(dataset_dir, updated_dataset_dir, get_jpg_image_names(dataset_dir))


products = {"Toilet":0, "Bathtub":1, "Sink":2, "Vanity":3, "Faucet":4, "Shelf":5}
create_yolo_training_config("updatedDataset", product_specific=False, product_type_list_names=["Toilet", "Bathtub", "Sink"]) #, "Vanity", "Faucet", "Shelf"
#create_yolo_training_config("updatedDataset", product_specific=True, product_type_id=products["Toilet"])

