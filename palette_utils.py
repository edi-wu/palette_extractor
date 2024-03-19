## Name: Eddie Wu
## Description: Module for functions related to palette image creation

from PIL import Image


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
