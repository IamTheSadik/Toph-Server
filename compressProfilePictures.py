import os
from PIL import Image

source_dir = "Data/ProfilePictures"
target_dir = source_dir + "/compressed"

# Create the target directory if it doesn't exist
os.makedirs(target_dir, exist_ok=True)

# Iterate over the files in the source directory
for filename in os.listdir(source_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        # Open the image
        image_path = os.path.join(source_dir, filename)
        image = Image.open(image_path)

        # Resize the image to a 1:1 aspect ratio
        width, height = image.size
        if width > height:
            new_width = height
            new_height = height
        else:
            new_width = width
            new_height = width

        # Ensure the maximum size is 250x250
        max_size = 250
        if new_width > max_size or new_height > max_size:
            new_width = max_size
            new_height = max_size

        resized_image = image.resize((new_width, new_height))

        # Save the compressed image in the target directory
        target_path = os.path.join(target_dir, filename)

        resized_image = image.resize((new_width, new_height))

        # Convert the image to RGB if it's not
        if resized_image.mode != 'RGB':
            resized_image = resized_image.convert('RGB')

        # Save the compressed image in the target directory
        target_path = os.path.join(target_dir, filename)
        resized_image.save(target_path, "JPEG", optimize=True, quality=80)

        # Close the image
        image.close()
        print(f"Compressed   @{filename.split('.')[0]}", end="\r")