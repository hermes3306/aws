import os
from PIL import Image

def make_background_transparent(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.png')

            # Open the image
            with Image.open(input_path) as img:
                # Convert image to RGBA if it's not already
                img = img.convert("RGBA")

                # Get image data
                datas = img.getdata()

                new_data = []
                for item in datas:
                    # If the pixel is white or very close to white, make it transparent
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                # Update the image with the new data
                img.putdata(new_data)

                # Save the image
                img.save(output_path, "PNG")
                print(f"Processed: {filename}")

if __name__ == "__main__":
    input_folder = "."
    output_folder = "."
    
    make_background_transparent(input_folder, output_folder)
    print("All images processed.")