## Name: Eddie Wu
## Description: Module for utility functions used in k-means

import random
from time import localtime, strftime
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000


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
# @param pixels_with_coords - list of pixels as lab color tuples
# @param k_colors - current representative pixels (list of RGB tuples, length k)
# @param k_clusters - current clusters of pixels (list of lists, each inner list is list of RGB tuples)
#
def group_pixels(pixels_with_coords, k_colors, k_clusters):
    # Iterate over pixels
    for i in range(len(pixels_with_coords)):
        # curr_pixel_with_coords = pixels_with_coords[i]
        # curr_pixel = curr_pixel_with_coords[1]
        curr_pixel = pixels_with_coords[i]
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
        # sq_euclidean_distance = get_sq_euclidean_dist(pixel, curr_k_color)
        # Update min distance and index of min as needed
        # if sq_euclidean_distance < min_distance:
        #     min_distance = sq_euclidean_distance
        #     idx_of_closest = i

        # Calculate distance using delta e cie2000
        pixel_obj = LabColor(pixel[0], pixel[1], pixel[2])
        curr_k_color_obj = LabColor(curr_k_color[0], curr_k_color[1], curr_k_color[2])
        dist = delta_e_cie2000(pixel_obj, curr_k_color_obj)
        if dist < min_distance:
            min_distance = dist
            idx_of_closest = i
    return idx_of_closest


## Helper function to calculate the squared Euclidean distance between two pixels
# @param pixel_1 - first pixel (RGB tuple)
# @param pixel_2 - second pixel (RGB tuple)
# @return the squared Euclidean distance (int)
#
def get_sq_euclidean_dist(pixel1, pixel2):
    return ((pixel1[0] - pixel2[0]) ** 2 +
            (pixel1[1] - pixel2[1]) ** 2 +
            (pixel1[2] - pixel2[2]) ** 2)


## Calculate the average color in each of k clusters
# @param k_clusters - clusters of pixels with coords (list of k lists, each list contains ((x, y), (r, g, b))
# @return list of k RGB tuples
#
def update_k_colors(k_clusters):
    result_k_colors = []
    for i in range(len(k_clusters)):
        curr_cluster = k_clusters[i]
        result_k_colors.append(get_average_pixel(curr_cluster))
    return result_k_colors


## Function to return an average pixel (average value in each channel) from a list of pixels
# @param cluster - list of pixel clusters (tuples of format ((x, y), (r, g, b))
# @return tuple of three ints for one pixel
#
def get_average_pixel(cluster):

    num_pixels = len(cluster)
    if num_pixels == 0:
        raise ZeroDivisionError("Cluster contains 0 pixels")
    pixels_list = []
    for i in range(num_pixels):
        pixels_list.append(cluster[i])
    sum_r, sum_g, sum_b = 0, 0, 0
    for pixel in pixels_list:
        sum_r += pixel[0]
        sum_g += pixel[1]
        sum_b += pixel[2]
    return (sum_r / num_pixels), (sum_g / num_pixels), (sum_b / num_pixels)


## Compares two lists of tuples for equality (same content in same order)
## Use delta e cie2000 distance (threshold 1.0) to check if colors are close enough
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
        # if list_1[i] != list_2[i]:
        #     return False
        color_1 = LabColor(list_1[i][0], list_1[i][1], list_1[i][2])
        color_2 = LabColor(list_2[i][0], list_2[i][1], list_2[i][2])
        dist = delta_e_cie2000(color_1, color_2)
        if dist > 1.0:
            return False
    return True


## Function to calculate total SSE (sum of squared errors) for the resulting clusters of a given k
# @param k_colors - the resulting representative k_colors (centroids)
# @param k_clusters - list of lists, where each list is a cluster of (coords, pixel) tuples
# @return sum of squared errors (squared Euclidean distances) between all pixels and their respective centroids
#
def get_total_SSE(k_colors, k_clusters):
    total_SSE = 0
    for i in range(len(k_colors)):
        centroid_pixel = k_colors[i]
        pixel_cluster = k_clusters[i]
        # Each pixel has format ((x, y), (r, g, b)) so need to use the RGB part
        for pixel in pixel_cluster:
            lab_color1 = LabColor(centroid_pixel[0], centroid_pixel[1], centroid_pixel[2])
            lab_color2 = LabColor(pixel[0], pixel[1], pixel[2])
            # total_SSE += get_sq_euclidean_dist(centroid_pixel, pixel)
            total_SSE += delta_e_cie2000(lab_color1, lab_color2)
    return total_SSE


## Function to generate a sortable timestamp string
# @return timestamp string in format yy/mm/dd h:m:s
#
def get_timestamp_str():
    return strftime("%Y_%m_%d_%H:%M:%S", localtime())


## Function to return weight of a pixel based on squared distance from nearest centroid
## NOW BASED ON delta e cie2000
# @param centroids - list of RGB tuples (centroids chosen so far)
# @param pixel - RGB tuple of pixel in question
#
def get_weight(centroids, pixel):
    min_distance = float("inf")
    for centroid in centroids:
        lab_color1 = LabColor(centroid[0], centroid[1], centroid[2])
        lab_color2 = LabColor(pixel[0], pixel[1], pixel[2])
        # distance = get_sq_euclidean_dist(centroid, pixel)
        distance = delta_e_cie2000(lab_color1, lab_color2)
        if distance < min_distance:
            min_distance = distance
    return min_distance
