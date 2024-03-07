## Name: Eddie Wu
## Date: 3/6/2024
## Description: Module for k-means clustering algorithm and helpers

from PIL import Image
import image_tools
import random


## Main function for running k-means algorithm on provided image
# @param file_path - full path of file received by server (string)
# @param k - number of clusters for k-means (int)
#
def run_k_means(file_path, k):
    print("Please wait... running k-means clustering.")
    # Open image, get pixel array, and establish bounds for coordinates
    with Image.open(file_path) as img:
        source_pixel_array = img.load()

        # Get the initial k colors (list of pixel tuples) by randomly selecting coordinates
        ## Coordinates' max value is 1 less than dimension
        k_random_coords = get_k_random_coords(k, img.width - 1, img.height - 1)
        k_colors = image_tools.map_coords_to_pixels(k_random_coords, source_pixel_array)

        # Print initial k_colors for debugging
        print("Initial k_colors (randomly selected): ", k_colors)

        # Convert the PixelAccess object (access using x and y coords) to a plain list of RGB tuples
        ## For rest of algorithm we need not consider x and y coords of any given pixel
        all_coords = []
        for x in range(img.width):
            for y in range(img.height):
                all_coords.append((x, y))
        source_pixel_tuples = image_tools.map_coords_to_pixels(all_coords, source_pixel_array)

        # Boolean for whether the result k_colors changed in last iteration
        result_changed = True

        # Run algorithm until result no longer changes
        while result_changed:

            # Make copy of last iteration's palette
            last_k_colors = k_colors[:]

            # Create empty list of lists for clusters
            k_clusters = [[] for _ in range(k)]

            # Place all pixels into clusters, each ith cluster corresponds to ith color in k_colors
            group_pixels(source_pixel_tuples, last_k_colors, k_clusters)

            # Update k_colors by getting new representative color from each cluster,
            ## where the representative color is the average color by RGB values
            k_colors = update_k_colors(k_clusters)

            # Compare updated result with past result and update change boolean as needed
            result_changed = not compare_tuple_lists(k_colors, last_k_colors)

    # Output resulting k_colors
    print("Representative k_colors: ", k_colors)

    # Create, display, and save an image showing the resulting palette
    palette_img = create_palette(k_colors)
    palette_img.show()
    palette_img.save("./results/palette.png")


## Returns k sets of distinct coordinates given specified bounds
# @param k - number of coordinates to return (int)
# @param max_x - max x value for coordinates (int)
# @param max_y - max y value for coordinates (int)
# @return list of k distinct (x, y) tuples
#
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
        result_k_colors.append(image_tools.get_average_pixel(curr_cluster))
    return result_k_colors


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
