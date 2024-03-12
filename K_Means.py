## Name: Eddie Wu
## Date: 3/6/2024
## Description: Class for k-means process


from PIL import Image
from Logger import Logger
import k_means_utils


class K_Means:
    ## Constructor
    # @param project_name - string for name of project/image
    # @param k - number of clusters
    # @param file_path - file path for source image
    # k_colors: list of RGB tuples
    # k_clusters: list of lists, each list contains RGB tuples
    # src_pixels: list of RGB tuples for all pixels in source image
    # iteration_num: number of current k_means iteration
    def __init__(self, project_name, k_value, file_path, log_file_name):
        self.project_name = project_name
        self.file_path = file_path
        self.log_file_name = log_file_name
        self.k = k_value
        self.k_colors = []
        self.k_clusters = [[] for _ in range(self.k)]
        self.src_pixels = []
        self.iteration_num = 0

    ## Main function to run k-means
    def run(self):
        print('Please wait... running k-means clustering.')
        with Image.open(self.file_path) as img, Logger(self.log_file_name) as logger:
            source_pixel_array = img.load()
            logger.log('Project Name: ' + self.project_name + '\n\n')

            # Get the initial k colors (list of pixel tuples) by randomly selecting coordinates
            ## Coordinates' max value is 1 less than dimension
            k_random_coords = k_means_utils.get_k_random_coords(self.k, img.width - 1, img.height - 1)
            self.k_colors = k_means_utils.map_coords_to_pixels(k_random_coords, source_pixel_array)

            # Print and log initial k_colors
            print("Initial k_colors (randomly selected): ", self.k_colors)
            logger.log("Initial k_colors (randomly selected): ")
            logger.log(k_means_utils.stringify_tuple_list(self.k_colors))

            # Convert the PixelAccess object (access using x and y coords) to a plain list of RGB tuples
            ## For rest of algorithm we need not consider x and y coords of any given pixel
            for x in range(img.width):
                for y in range(img.height):
                    self.src_pixels.append(source_pixel_array[x, y])

            # Boolean for whether the result k_colors changed in last iteration
            result_changed = True

            # Run algorithm until result no longer changes
            while result_changed:
                # Make copy of last iteration's palette
                last_k_colors = self.k_colors[:]

                # Place all pixels into clusters, each ith cluster corresponds to ith color in k_colors
                k_means_utils.group_pixels(self.src_pixels, self.k_colors, self.k_clusters)

                # Update k_colors by getting new representative color from each cluster,
                ## where the representative color is the average color by RGB values
                self.k_colors = k_means_utils.update_k_colors(self.k_clusters)

                # Log updated k_colors with iteration number
                self.iteration_num += 1
                logger.log("[ " + str(self.iteration_num) + "]: " + k_means_utils.stringify_tuple_list(self.k_colors))

                # Compare updated result with past result and update change boolean as needed
                result_changed = not k_means_utils.compare_tuple_lists(self.k_colors, last_k_colors)

            # Print and log resulting k_colors
            print("Representative k_colors: ", self.k_colors)
            logger.log("Representative k_colors: ")
            logger.log(k_means_utils.stringify_tuple_list(self.k_colors))

        # Create, display, and save an image showing the resulting palette
        palette_img = k_means_utils.create_palette(self.k_colors)
        palette_img.show()
        palette_img.save("./results/palette.png")
