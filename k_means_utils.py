## Name: Eddie Wu
## Date: 3/6/2024
## Description: Module for utility functions used in k-means

from PIL import Image
import random


## Returns k sets of distinct coordinates given specified bounds
# @param k - number of coordinates to return (int)
# @param max_x - max x value for coordinates (int)
# @param max_y - max y value for coordinates (int)
# @return list of k distinct (x, y) tuples
def get_k_random_coords(k, max_x, max_y):
    # Initially, use a set to ensure all random coord tuples are distinct # work on making rgb values distinct
    result_set = set()
    # Populate the set until it reaches k size
    while len(result_set) < k:
        rand_x = random.randint(0, max_x)
        rand_y = random.randint(0, max_y)
        result_set.add((rand_x, rand_y))
    # Return result set converted to list
    return list(result_set)


## Function to map a list of coordinates tuples to pixel tuples
# @param coords_list - list of (x, y) coordinates (list of tuples)
# @param pixel_array - array of pixels from an image (list of tuples)
# @return list of pixel tuples corresponding to coordinates provided
def map_coords_to_pixels(coords_list, pixel_array):
    pixels_list = []
    for x, y in coords_list:
        pixels_list.append(pixel_array[x, y])
    return pixels_list


## Stringifies a list of RGB tuples for printing or logging
# @param pixels_list - list of RGB tuples
# @return stringified list
def stringify_tuple_list(pixels_list):
    return '  '.join([str(t) for t in pixels_list])


## Places pixels from source array into appropriate cluster based on k_colors
# @param pixels - source pixels array (list of RGB tuples)
# @param k_colors - current representative pixels (list of RGB tuples, length k)
# @param k_clusters - current clusters of pixels (list of lists, each inner list is list of RGB tuples)
#
def group_pixels(pixels, k_colors, k_clusters):
    # Iterate over pixels
    for i in range(len(pixels)):
        curr_pixel = pixels[i]
        # Get the cluster index for current pixel based on min. squared Euclidean distance
        cluster_idx = get_cluster_id(curr_pixel, k_colors)
        # Place the pixel in the corresponding cluster
        k_clusters[cluster_idx].append(curr_pixel)


## Determine the closest representative color to a given pixel
# @param pixel - RGB values to compare against k_colors (list of RGB tuples)
# @param k_colors - current representative pixels (list of RGB tuples, length k)
# @return index of color in k_colors list that is closest to current pixel (int)
#
def get_cluster_id(pixel, k_colors):
    # Variables to track min distance and index of min
    idx_of_closest = -1
    min_distance = float("inf")
    # Iterate over k_colors
    for i in range(len(k_colors)):
        curr_k_color = k_colors[i]
        # Calculate squared Euclidean distance between pixel and current k_color
        sq_euclidean_distance = ((pixel[0] - curr_k_color[0]) ** 2
                                 + (pixel[1] - curr_k_color[1]) ** 2
                                 + (pixel[2] - curr_k_color[2]) ** 2)
        # Update min distance and index of min as needed
        if sq_euclidean_distance < min_distance:
            min_distance = sq_euclidean_distance
            idx_of_closest = i
    return idx_of_closest


## Calculate the average color in each of k clusters
# @param k_clusters - clusters of pixels (list of k lists, each list contains RGB tuples)
# @return list of k RGB tuples
#
def update_k_colors(k_clusters):
    result_k_colors = []
    for i in range(len(k_clusters)):
        curr_cluster = k_clusters[i]
        result_k_colors.append(get_average_pixel(curr_cluster))
    return result_k_colors


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


## Compares two lists of tuples for equality (same content in same order)
# @param list_1 - first list of tuples
# @param list_2 - second list of tuples
# @return True if lists contain the same content, False otherwise
#
def compare_tuple_lists(list_1, list_2):
    # Check for length equality first
    if len(list_1) != len(list_2):
        return False
    # Check equality of each tuple in order
    for i in range(len(list_1)):
        if list_1[i] != list_2[i]:
            return False
    return True


## Creates a png image consisting of bands of the representative k_colors
# @param k_colors - resulting k_colors from k-means clustering (list of RGB tuples)
# @return PIL image object of a png with vertical bands, one for each k_color
#
def create_palette(k_colors):
    # Default dimensions for palette--can be adjusted later
    IMG_HEIGHT = 200
    WIDTH_PER_COLOR = 100

    # Create initial black image and get its pixels array (PIL PixelAccess object)
    img = Image.new("RGB", (WIDTH_PER_COLOR * len(k_colors), IMG_HEIGHT))
    pixel_array = img.load()

    # Update image with colors
    for i in range(len(k_colors)):
        curr_color = k_colors[i]

        # Determine min and max x value of each color strip
        curr_min_x = WIDTH_PER_COLOR * i
        curr_max_x = curr_min_x + WIDTH_PER_COLOR

        # Fill each vertical strip with the right color
        for x in range(curr_min_x, curr_max_x):
            for y in range(IMG_HEIGHT):
                pixel_array[x, y] = curr_color

    return img
