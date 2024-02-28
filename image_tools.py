## Name: Eddie Wu
## Date: 2/20/2024
## Description: Functions for image processing

from PIL import Image


## Main image processing function that calls appropriate helper based on option choice
# @param file_path - path to source image file (string)
# @param option - image processing option (integer)
# @param ld_option - *for lighten/darken* 'L' or 'D' for lighten or darken (string)
# @param amount - *for lighten/darken* percentage between 0-100 to adjust image by (integer)
# @param channel - *for channel color* 'R' 'G' or 'B' channel (string)
# @param pixel_array - *for add blur* pixel array for source image (list of tuples)
#
def process_image(file_path, option, ld_option='', amount=0, channel=''):
    # Print status message for processing in progress
    print("Please wait... your image is being processed.")
    # Open image for processing
    with Image.open(file_path) as img:
        # Create black copy and load both pixel arrays
        altered_img = copy_image(img)
        source_pixels = img.load()
        altered_pixels = altered_img.load()
        # Nested loop to process pixel by pixel
        for x in range(img.width):
            for y in range(img.height):
                # Get source pixel and its RGB values
                old_pixel = source_pixels[x, y]
                # Get new pixel's RGB values based on which processing option is chosen
                # 1 - lighten/darken
                # 2 - channel color
                # 3 - invert colors
                # 4 - add blur
                # 5 - edge detection
                new_pixel = (0, 0, 0)
                if option == 1:
                    new_pixel = adjust_brightness(old_pixel, ld_option, amount)
                elif option == 2:
                    new_pixel = channel_color(old_pixel, channel)
                elif option == 3:
                    new_pixel = invert_colors(old_pixel)
                elif option == 4:
                    new_pixel = add_blur(x, y, img.width, img.height, source_pixels)
                elif option == 5:
                    new_pixel = detect_edges(old_pixel, x, y, img.width, img.height, source_pixels)
                # Update altered pixel array
                altered_pixels[x, y] = new_pixel
        # Display altered image and prompt user to save or not
        show_and_save(altered_img, file_path)


## Create a copy of the provided image with all black color
# @param img - source image (PIL image object)
# @return PIL image object that has same size and mode as source
#
def copy_image(img):
    return Image.new(img.mode, img.size, color=(0, 0, 0))


## Calculates new RGB values based on lighten/darken amount
# @param pixel - RGB values of source pixel (tuple of three ints)
# @param option - 'L' or 'D' for lighten or darken operation (string)
# @param amount - percentage amount to adjust by (int)
# @return RGB values of altered pixel (tuple of three ints)
#
def adjust_brightness(pixel, option, amount):
    ## To lighten, adjust each value by % difference between 255 and the lowest of the three values
    ## To darken, adjust each value by % difference between 0 and the highest of the three values
    # Convert pixel tuple to dict with RGB as keys
    pixel_dict = {'R': pixel[0], 'G': pixel[1], 'B': pixel[2]}
    if option.upper() == 'L':
        BOUND = 255
        # Get the lowest value from the three channels
        lowest_value = min(pixel)
        # Process to obtain adjustment
        distance = BOUND - lowest_value
        potential_adjustment = round(amount / 100 * distance)
        # Get the updated value within bounds
        lowest_value_updated = min(lowest_value + potential_adjustment, BOUND)
        # Get adjustment percentage for other values
        # NB: if distance is 0 i.e. lowest RGB value is already at BOUND, no adjust will occur
        actual_adjustment = lowest_value_updated - lowest_value
        increase_percentage = 0 if distance == 0 else actual_adjustment / distance
        # Update the lowest value in dict to the new value, and update other values using the percentage
        for (key, value) in pixel_dict.items():
            if value == lowest_value:
                pixel_dict[key] = lowest_value_updated
            else:
                pixel_dict[key] = round(value + (BOUND - value) * increase_percentage)

    elif option.upper() == 'D':
        # Same idea as lighten except adjust toward lower bound of 0
        BOUND = 0

        highest_value = max(pixel)
        distance = highest_value - BOUND
        potential_adjustment = round(amount / 100 * distance)

        highest_value_updated = max(highest_value - potential_adjustment, BOUND)
        actual_adjustment = highest_value - highest_value_updated
        decrease_percentage = 0 if distance == 0 else actual_adjustment / distance

        for (key, value) in pixel_dict.items():
            if value == highest_value:
                pixel_dict[key] = highest_value_updated
            else:
                pixel_dict[key] = round(value - (value - BOUND) * decrease_percentage)

    # Return the updated RGB values as a tuple
    return pixel_dict['R'], pixel_dict['G'], pixel_dict['B']


## Create new pixel reflecting intensity of specified color channel
# @param pixel - RGB values of source pixel (tuple of three ints)
# @param channel - 'R', 'G' or 'B' for color channel (string)
# @return RGB values of altered pixel (tuple of three ints)
#
def channel_color(pixel, channel):
    # Set all values to the intensity of specified channel
    pixel_r, pixel_g, pixel_b = pixel[0], pixel[1], pixel[2]
    if channel == 'R':
        return pixel_r, pixel_r, pixel_r
    elif channel == 'G':
        return pixel_g, pixel_g, pixel_g
    else:
        return pixel_b, pixel_b, pixel_b


## Create new pixel with inverted colors
# @param pixel - RGB values of source pixel (tuple of three ints)
# @return RGB values of altered pixel (tuple of three ints)
#
def invert_colors(pixel):
    # For each value, update it to result of 255 - value
    pixel_r, pixel_g, pixel_b = pixel[0], pixel[1], pixel[2]
    return 255 - pixel_r, 255 - pixel_g, 255 - pixel_b


## Add blur by averaging RGB channel values
# @param pixel_x - x coordinate of pixel (int)
# @param pixel_y - y coordinate of pixel (int)
# @param max_x - width of image (int)
# @param max_y - height of image (int)
# @param pixel_array - array of pixels from source image (list of tuples)
# @return RGB values of altered pixel (tuple of three ints)
#
def add_blur(pixel_x, pixel_y, max_x, max_y, pixel_array):
    # Get valid coordinates for neighbor pixels
    neighbor_coords = get_valid_neighbors(pixel_x, pixel_y, max_x, max_y)
    # Map list of coordinates to list of pixels
    neighbor_pixels = map_coords_to_pixels(neighbor_coords, pixel_array)
    # Calculate and return average value of each channel for neighbors
    return get_average_pixel(neighbor_pixels)


## Function to convert image to a black and white image showing edges
## Do this by coloring black all pixels whose RGB distance from the average of its neighbors exceeds 30
## (dist = |r - r_neighbor_avg| + |g - g_neighbor_avg| + |b - b_neighbor_avg|)
## Color all other pixels white
## Procedure taken from textbook exercises P4.53 and P4.54
# @param pixel - RGB values for current pixel (tuple of three ints)
# @param pixel_x - x coordinate of pixel (int)
# @param pixel_y - y coordinate of pixel (int)
# @param max_x - width of image (int)
# @param max_y - height of image (int)
# @param pixel_array - array of pixels from source image (list of tuples)
# @return either a black or white pixel tuple
#
def detect_edges(pixel, pixel_x, pixel_y, max_x, max_y, pixel_array):
    # Get valid coordinates for neighbor pixels
    neighbor_coords = get_valid_neighbors(pixel_x, pixel_y, max_x, max_y)
    # Map list of coordinates to list of pixels
    neighbor_pixels = map_coords_to_pixels(neighbor_coords, pixel_array)
    # Calculate average RGB values of neighbor pixels
    average_neighbor = get_average_pixel(neighbor_pixels)
    # Calculate distance between current pixel's RGB and average neighbor's RGB
    dist = get_rgb_distance(pixel, average_neighbor)
    # Change pixel to black or white based on dist > 30
    return (0, 0, 0) if dist > 30 else (255, 255, 255)


## Function to return coordinates of a pixel's 8 neighbors
# @param pixel_x - x coordinate of center pixel (int)
# @param pixel_y - y coordinate of center pixel (int)
# @param max_x - width of image (int)
# @param max_y - height of image (int)
# @return list of up to 8 (x, y) tuples for valid neighbors
#
def get_valid_neighbors(pixel_x, pixel_y, max_x, max_y):
    neighbors = []
    neighbor_x, neighbor_y = -1, -1
    # Nested loop to get all neighbors via offsetting by -1, 0, 1
    for x_offset in range(-1, 2, 1):
        for y_offset in range(-1, 2, 1):
            # Skip center pixel itself
            if x_offset == 0 and y_offset == 0:
                continue
            # Update neighbor coords
            neighbor_x = pixel_x + x_offset
            neighbor_y = pixel_y + y_offset
            # Skip if neighbor coords are out of bounds
            if neighbor_x >= max_x or neighbor_x < 0 or neighbor_y >= max_y or neighbor_y < 0:
                continue
            # Add neighbor coords as tuple to list
            neighbors.append((neighbor_x, neighbor_y))
    return neighbors


## Function to map a list of coordinates tuples to pixel tuples
# @param coords_list - list of (x, y) coordinates (list of tuples)
# @param pixel_array - array of pixels from an image (list of tuples)
# @return list of pixel tuples corresponding to coordinates provided
#
def map_coords_to_pixels(coords_list, pixel_array):
    pixels_list = []
    for x, y in coords_list:
        pixels_list.append(pixel_array[x, y])
    return pixels_list


## Function to return an average pixel (average value in each channel) from a list of pixels
# @param pixels_list - list of pixels (tuples of three ints)
# @return tuple of three ints for one pixel
#
def get_average_pixel(pixels_list):
    num_pixels = len(pixels_list)
    sum_r, sum_g, sum_b = 0, 0, 0
    for pixel in pixels_list:
        sum_r += pixel[0]
        sum_g += pixel[1]
        sum_b += pixel[2]
    return round(sum_r / num_pixels), round(sum_g / num_pixels), round(sum_b / num_pixels)


## Function to calculate RGB distance between two pixels
## Formula: (dist = |r - r_neighbor_avg| + |g - g_neighbor_avg| + |b - b_neighbor_avg|)
# @param pixel_a - first pixel (tuple of three ints)
# @param pixel_b - second pixel (tuple of three ints)
# @return distance between RGB values (int)
#
def get_rgb_distance(pixel_a, pixel_b):
    return abs(pixel_a[0] - pixel_b[0]) + abs(pixel_a[1] - pixel_b[1]) + abs(pixel_a[2] - pixel_b[2])

## Function to display altered image and prompt user to save
# @param img - altered image object for display (PIL image object)
# @param file_path - path to source image file (string)
#
def show_and_save(img, file_path):
    NAME_SUFFIX = '_saved'
    # Display image
    img.show()
    # Prompt user to choose to save
    user_choice = input("Do you want to save the altered image? (Y/N): ")
    if user_choice.upper() == 'Y':
        # Separate directory from file name (w/ extension)
        path_parts = file_path.rsplit("/", 1)
        directory, file_name = path_parts[0], path_parts[1]
        # Separate file name from extension
        name_and_extension = file_name.rsplit(".", 1)
        # Assemble new file path
        save_file_path = directory + "/" + name_and_extension[0] + NAME_SUFFIX + "." + name_and_extension[1]
        # Save the altered image
        img.save(save_file_path)
