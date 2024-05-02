## Name: Eddie Wu
## Description: Class for k-means process


from PIL import Image, ImageCms
from Logger import Logger
from time import perf_counter
from matplotlib import pyplot as plt
from random import choices
import k_means_utils
import palette_utils


class K_Means:
    ## Constructor
    # @param project_name - string for name of project/image
    # @param k_values - tuple (start, end, interval) for number of clusters
    # @param file_path - file path for source image
    # @param num_runs - int number of runs for this image
    # @param log_file_name - string for the log file name
    # @param img_extension - string for the extension of the original image
    # @param palette_replace - bool for whether to create copies of original with colors replaced by palette colors
    # @param do_resize - int for % to resize down to; default is 100
    # src_pixels: list of coords & RGB tuples ((x, y), (r, g, b)) for the source image
    # k_colors: list of RGB tuples
    # k_clusters: list of lists, each list contains a tuple of coords and RGB values ((x, y), (r, g, b))
    # SSE: dict mapping k value to list of longs, each list logs SSE of each run at that k value
    # total_time: total time elapsed in seconds for suite of runs
    # result_img_path: path to result image for server response
    def __init__(self, project_name, k_values, file_path, num_runs, log_file_name, img_extension, palette_replace, resize_level):
        self.project_name = project_name
        self.file_path = file_path
        self.k_values = k_values
        self.num_runs = num_runs
        self.log_file_name = log_file_name
        self.img_extension = img_extension
        self.palette_replace = palette_replace
        self.resize_level = resize_level

        self.src_pixels_with_coords = []
        self.k_colors = []
        self.k_clusters = [[]]
        self.SSE = {}
        self.total_time = 0
        self.result_img_path = ''

    ## Main function to run k-means
    def run(self):
        print('\nPlease wait... running k-means clustering.')

        with Image.open(self.file_path) as img, Logger(self.log_file_name) as logger:

            logger.log('Project Name: ' + self.project_name + '\n\n')

            if self.resize_level < 100:
                resize_fraction = self.resize_level / 100
                img = img.resize((round(img.width * resize_fraction), round(img.height * resize_fraction)))

            # Convert to lab space
            srgb_p = ImageCms.createProfile("sRGB")
            lab_p = ImageCms.createProfile("LAB")
            rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
            lab_img = ImageCms.applyTransform(img, rgb2lab)

            # Load image array
            # src_image_array = img.load()
            print(f"image mode: {lab_img.mode}")
            src_image_array = lab_img.load()
            img_height, img_width = lab_img.height, lab_img.width

            # Obtain list of pixels as RGB tuples
            for x in range(img_width):
                for y in range(img_height):
                    self.src_pixels_with_coords.append(((x, y), (src_image_array[x, y])))

            # Loop to run n times for specified values of k (single or ranged)
            k_start, k_end, k_interval = self.k_values
            # Initialize elements in SSE dict to empty lists
            for k in range(k_start, k_end + 1, k_interval):
                self.SSE[k] = []
            for run_num in range(self.num_runs):
                logger.log(f"{'~' * 6} Run #{run_num + 1} of {self.num_runs} {'~' * 6}\n")
                for k in range(k_start, k_end + 1, k_interval):
                    logger.log("k = " + str(k))
                    # Initialize k_clusters based on current k value
                    self.k_clusters = [[] for _ in range(k)]
                    try:
                        # Run k-means algorithm
                        self.run_k_means(src_image_array, img_height, img_width, k, logger)
                        # Create result visualization
                        self.result_img_path = self.visualize_results(src_image_array, img.mode, img_width, img_height, run_num, k)
                        # Calculate and log total SSE for the given k
                        sse_value = k_means_utils.get_total_SSE(self.k_colors, self.k_clusters)
                        self.SSE[k].append(sse_value)
                        logger.log(f"SSE: {sse_value} (k = {k})")
                        logger.log(f"\n{'~' * 18}\n")
                    except Exception as e:
                        print('Quitting current run due to error: ' + str(e))
                        logger.log('Quitting current run due to error: ' + str(e))
                    finally:
                        # Clean up to reset k_colors for next run
                        self.k_colors = []

            # Perform any necessary cleanup / analysis / plotting
            # Plot total SSE against k if used a range of k values
            if k_start != k_end:
                self.plot_SSE()

            # Log total time elapsed for this suite of runs
            logger.log(f"Summary: \nNumber of runs: {self.num_runs}\n"
                       f"k_start: {k_start}; k_end: {k_end}; k_interval: {k_interval}\n"
                       f"Total time elapsed: {self.total_time} seconds.")

        return self.result_img_path

    ## Runs k-means clustering algorithm once
    # @param src_image_array - PixelAccess array for source images
    # @param h - height of image (int)
    # @param w - width of image (int)
    # @param k - int for current value of k
    # @param logger - instance of logger
    def run_k_means(self, src_image_array, h, w, k, logger):
        # Use perf counter to track start time
        start_time = perf_counter()
        print('\nRunning k-means with k = ' + str(k))

        # Test exception handling and logging
        # if k % 2 == 0:
        #     raise ValueError("Testing quitting and logging exception, k = " + str(k))

        # Method 1: Get the initial k colors (list of pixel tuples) by randomly selecting coordinates
        ## Coordinates' max value is 1 less than dimension
        ## Consider putting this in a function to use with switch statement
        # k_random_coords = k_means_utils.get_k_random_coords(k, w - 1, h - 1)
        # self.k_colors = k_means_utils.map_coords_to_pixels(k_random_coords, src_image_array)

        # Print and log initial k_colors
        # print("Initial k_colors (randomly selected): ", self.k_colors)
        # logger.log("Initial k_colors (randomly selected): ")
        # logger.log(k_means_utils.stringify_tuple_list(self.k_colors) + '\n')

        # Method 2: Get initial k colors via k-means++ selection
        kmpp_start_time = perf_counter()
        self.run_k_means_plus_plus(k)
        kmpp_stop_time = perf_counter()
        logger.log(f"Time elapsed for k-means++: {kmpp_stop_time - kmpp_start_time} seconds")

        # Print and log initial k_colors
        print("Initial k_colors (k-means++): ", self.k_colors)
        logger.log("Initial k_colors (k-means++): ")
        logger.log(k_means_utils.stringify_tuple_list(self.k_colors) + '\n')

        # Iteration number for logging
        iteration_num = 0
        # Boolean for whether the result k_colors changed in last iteration
        result_changed = True

        # Run algorithm until result no longer changes
        while result_changed:
            # Make copy of last iteration's palette
            last_k_colors = self.k_colors[:]

            # Place all pixels into clusters, each ith cluster corresponds to ith color in k_colors
            k_means_utils.group_pixels(self.src_pixels_with_coords, self.k_colors, self.k_clusters)

            # Update k_colors by getting new representative color from each cluster,
            ## where the representative color is the average color by RGB values
            self.k_colors = k_means_utils.update_k_colors(self.k_clusters)

            # Log updated k_colors with iteration number
            iteration_num += 1
            logger.log("[ " + str(iteration_num) + "]: " + k_means_utils.stringify_tuple_list(self.k_colors))

            # Compare updated result with past result and update change boolean as needed
            result_changed = not k_means_utils.compare_tuple_lists(self.k_colors, last_k_colors)

        # Print and log resulting k_colors
        print("Representative k_colors: ", self.k_colors)
        logger.log("\nRepresentative k_colors: ")
        logger.log(k_means_utils.stringify_tuple_list(self.k_colors) + '\n')

        # Use perf counter for end time and log time elapsed
        stop_time = perf_counter()
        time_elapsed = stop_time - start_time
        self.total_time += time_elapsed
        logger.log("Time elapsed for k-means algorithm: " + str(time_elapsed) + " seconds\n")

    ## Function to update self.k_colors with k initial centroids using k-means++
    # @param k - int value of k for current run
    #
    def run_k_means_plus_plus(self, k):
        print(f"Running k_means++ to select {k} centroids\n")
        # Initially select one pixel at random
        ## NB choices returns list of 1 item by default, use [0] to access pixel, [1] to access its RGB tuple
        self.k_colors.append(choices(self.src_pixels_with_coords)[0][1])
        # Create list of weights proportional to sq dist of each pixel to nearest selected center
        weights = []
        for i in range(len(self.src_pixels_with_coords)):
            curr_pixel = self.src_pixels_with_coords[i][1]
            weights.append(k_means_utils.get_weight(self.k_colors, curr_pixel))
        # While not k have been chosen:
        while len(self.k_colors) < k:
            # Choose next center
            self.k_colors.append(choices(self.src_pixels_with_coords, weights=weights)[0][1])
            # Update weights
            for i in range(len(self.src_pixels_with_coords)):
                curr_pixel = self.src_pixels_with_coords[i][1]
                weights[i] = k_means_utils.get_weight(self.k_colors, curr_pixel)

    ## Function to create result images showing the palette
    # @param src_image_array - image array of source image
    # @param mode - mode of source image (used for making a copy)
    # @param img_width - width of original image (used for making a copy)
    # @param img_height - height of original image (used for making a copy)
    # @param run_num - number of the current run (used in image path)
    # @param k - k value of current run (used in image path)
    #
    def visualize_results(self, src_image_array, mode, img_width, img_height, run_num, k):
        # Create the palette appended to original image
        palette_img_path = (f"./results/{k_means_utils.get_timestamp_str()}__{self.project_name}_run_{run_num + 1}_k_"
                            f"{k}{self.img_extension}")
        # palette_img_path = f"./results/{self.project_name}{self.img_extension}"
        palette_img = palette_utils.create_appended_palette(src_image_array, mode, img_width, img_height,
                                                            self.k_colors, self.k_clusters)
        palette_img.save(palette_img_path)
        palette_img.close()

        # Create copy of original with pixels replaced by representative colors
        if self.palette_replace:
            reduced_image_path = (f"./results/{k_means_utils.get_timestamp_str()}__{self.project_name}_[r]_run_"
                                  f"{run_num + 1}_k_{k}{self.img_extension}")
            reduced_image = palette_utils.create_reduced_image(mode, img_width, img_height,
                                                               self.k_clusters, self.k_colors)
            reduced_image.save(reduced_image_path)
            reduced_image.close()

        # Return palette image path for server
        return palette_img_path

    ## Plots SSE against k values
    #
    def plot_SSE(self):
        # Create lists for x and y axes
        x = []
        y = []
        # Get start, end, and interval for k
        k_start, k_end, k_interval = self.k_values
        # Append k to x-axis values
        # Append average of SSE for a given k to y-axis values
        # Divide SSE values by a constant factor (million) for y-axis data
        for k in range(k_start, k_end + 1, k_interval):
            x.append(k)
            y.append((sum(self.SSE[k]) / len(self.SSE[k])) / (10 ** 6))
        # Create the plot
        plt.plot(x, y, '-o')
        plt.xlabel("k")
        plt.ylabel("SSE (millions)")
        # Save plot to file using appropriate path
        plot_path = (f"./plots/{k_means_utils.get_timestamp_str()}__{self.project_name}_{self.num_runs}x_"
                     f"k_({k_start}_{k_end}_{k_interval}).png")
        plt.savefig(plot_path)
        # plt.show()
