## Name: Eddie Wu
## Description: Module for functions related to palette image creation

from PIL import Image, ImageCms


## Creates basic palette bands image
# @param k_colors - resulting k_colors from k-means clustering (list of RGB tuples)
# @return PIL image object of a copy of original image, with all pixels replaced by their representative
#
def create_basic_palette(k_colors):
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


## Creates copy of the original image with proportional palette bands appended
# @param src_image_array - image array for original image
# @param mode - mode of original image (used to make copy)
# @param img_width - width of original image
# @param img_height - height of original image
# @param k_colors - resulting k_colors from k-means clustering (list of RGB tuples)
# @param k_clusters - resulting k_clusters for each representative color (used for proportional palette bands)
# @return PIL image object of a png with vertical bands, one for each k_color
#
def create_appended_palette(src_image_array, mode, img_width, img_height, k_colors, k_clusters):
    # Create underlying "canvas" with enough room for the palette section
    # Make a white gap of 25 px between image and palette
    # Make palette dimension 1/2 of image dimension, minimum 50 px
    GAP = 25
    MIN_PALETTE_DIMENSION = 50
    canvas_width, canvas_height = img_width, img_height
    shorter_dimension = min(img_width, img_height)
    longer_dimension = max(img_height, img_width)
    orientation = ''
    if canvas_width == shorter_dimension:
        canvas_width = canvas_width + GAP + max(MIN_PALETTE_DIMENSION, round(shorter_dimension / 2))
        orientation = 'P'
    else:
        canvas_height = canvas_height + GAP + max(MIN_PALETTE_DIMENSION, round(shorter_dimension / 2))
        orientation = 'L'

    # Create copy of original image, initially all white (255, 128, 128) in PIL LAB transform
    result_img = Image.new(mode, (canvas_width, canvas_height), color=(255, 128, 128))
    result_img_array = result_img.load()

    # Write original image to canvas
    for x in range(img_width):
        for y in range(img_height):
            result_img_array[x, y] = src_image_array[x, y]

    # Map k_clusters to a proportional length value in pixels
    k_colors_lengths = []
    for i in range(len(k_clusters)):
        k_colors_lengths.append(len(k_clusters[i]))
    total_pixels = sum(k_colors_lengths)
    for i in range(len(k_colors_lengths)):
        k_colors_lengths[i] = round((k_colors_lengths[i] / total_pixels) * longer_dimension)
    # Fudge the last band a bit to avoid any gaps at the bottom
    k_colors_lengths[len(k_colors_lengths) - 1] = longer_dimension - sum(k_colors_lengths[:-1])

    # Associate the lengths with each k_color, sorted in descending order
    map_length_to_color = {}
    for i in range(len(k_colors_lengths)):
        map_length_to_color[k_colors_lengths[i]] = k_colors[i]
    sorted_length_color_tuples = sorted(map_length_to_color.items(), reverse=True)
    # print(f"the sorted palette band lengths are: {sorted_length_color_tuples}")

    # Write the palette section onto canvas based on orientation
    if orientation == 'P':
        x_start, y_start = img_width + GAP - 1, 0
        for i in range(len(sorted_length_color_tuples)):
            curr_color = sorted_length_color_tuples[i][1]
            # Write a palette band whose height is proportional to cluster size
            for x in range(x_start, canvas_width):
                for y in range(y_start, y_start + sorted_length_color_tuples[i][0]):
                    result_img_array[x, y] = curr_color
            # Update start point of y coordinate
            y_start += sorted_length_color_tuples[i][0]

    elif orientation == 'L':
        x_start, y_start = 0, img_height + GAP - 1
        for i in range(len(sorted_length_color_tuples)):
            curr_color = sorted_length_color_tuples[i][1]
            # Write a palette band whose width is proportional to cluster size
            for x in range(x_start, x_start + sorted_length_color_tuples[i][0]):
                for y in range(y_start, canvas_height):
                    result_img_array[x, y] = curr_color
            # Update start point of y coordinate
            x_start += sorted_length_color_tuples[i][0]

    srgb_p = ImageCms.createProfile("sRGB")
    lab_p = ImageCms.createProfile("LAB")
    lab2rgb = ImageCms.buildTransformFromOpenProfiles(lab_p, srgb_p, "LAB", "RGB")
    result_img = ImageCms.applyTransform(result_img, lab2rgb)

    return result_img


## Creates a copy of the original image except that all pixels have been replaced by
## the representative color of their cluster
# @param mode - mode of original image (used to make copy)
# @param img_width - width of original image
# @param img_height - height of original image
# @param k_clusters - clusters of coords, pixel tuples
# @param k_colors - resulting k_colors from k-means clustering (list of RGB tuples)
# @return PIL image object of a copy of original image, with all pixels replaced by their representative
#
def create_reduced_image(mode, img_width, img_height, k_clusters, k_colors):
    result_img = Image.new(mode, (img_width, img_height), color=(255, 128, 128))
    result_img_array = result_img.load()

    for i in range(len(k_colors)):
        replacement_color = k_colors[i]
        pixel_cluster = k_clusters[i]
        for pixel in pixel_cluster:
            x, y = pixel[0]
            result_img_array[x, y] = replacement_color

    srgb_p = ImageCms.createProfile("sRGB")
    lab_p = ImageCms.createProfile("LAB")
    lab2rgb = ImageCms.buildTransformFromOpenProfiles(lab_p, srgb_p, "LAB", "RGB")
    result_img = ImageCms.applyTransform(result_img, lab2rgb)

    return result_img
