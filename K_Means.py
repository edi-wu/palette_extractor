## Name: Eddie Wu
## Description: Class for k-means process


from PIL import Image, ImageOps
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
    # src_pixels_with_coords: list of coords & LAB tuples ((x, y), (r, g, b)) for the source image
    # src_pixels_with_freq: list of lists, each smaller list contains LAB tuples and their freq. i.e. [(L, a, b), n]
    # k_colors: list of LAB tuples
    # k_clusters: list of lists, each list contains LAB tuple and its freq: [(L, a, b), n]
    # k_clusters_sizes: list of ints corresponding to size of each cluster (sum of each color * its frequency)
    # SSE: dict mapping k value to list of longs, each list logs SSE of each run at that k value
    # total_time: total time elapsed in seconds for suite of runs
    # result_img_path: path to result image for server response
    def __init__(self, project_name, k_values, file_path, num_runs, log_file_name, img_extension, palette_replace,
                 resize_level):
        self.project_name = project_name
        self.file_path = file_path
        self.k_values = k_values
        self.num_runs = num_runs
        self.log_file_name = log_file_name
        self.img_extension = img_extension
        self.palette_replace = palette_replace
        self.resize_level = resize_level

        self.src_pixels_with_coords = []  # Now not used
        self.src_pixels_with_freq = []
        self.k_colors = []
        self.k_clusters = [[]]
        self.k_clusters_sizes = []
        self.SSE = {}
        self.total_time = 0
        self.result_img_path = ''

    ## Main function to run k-means
    def run(self):
        run_start_time = perf_counter()
        print('\nPlease wait... running k-means clustering.')

        with Image.open(self.file_path) as img, Logger(self.log_file_name) as logger:
            img = ImageOps.exif_transpose(img)
            logger.log('Project Name: ' + self.project_name + '\n\n')

            if self.resize_level < 100:
                resize_fraction = self.resize_level / 100
                img = img.resize((round(img.width * resize_fraction), round(img.height * resize_fraction)))

            # Load image array and get dimensions
            src_image_array = img.load()
            img_height, img_width = img.height, img.width

            print(f"Number of pixels in the image: {img_width * img_height}")
            logger.log(f"Number of pixels in the image: {img_width * img_height}\n")

            # Generate frequency map
            pixel_freq_map = {}
            for x in range(img_width):
                for y in range(img_height):
                    rgb_tuple = src_image_array[x, y]
                    pixel_freq_map[rgb_tuple] = pixel_freq_map.get(rgb_tuple, 0) + 1

            # Create list of RGB tuples with frequency
            for k, v in pixel_freq_map.items():
                self.src_pixels_with_freq.append([k, v])

            # Check print first 10
            # for i in range(10):
            #     print(self.src_pixels_with_freq[i])

            print(f"Number of colors to process: {len(self.src_pixels_with_freq)}")
            logger.log(f"Number of colors to process: {len(self.src_pixels_with_freq)}\n")

            # Convert pixel portion of each tuple to LAB color space
            for i in range(len(self.src_pixels_with_freq)):
                # Convert the RGB tuple to a LAB tuple
                self.src_pixels_with_freq[i][0] = k_means_utils.rgb_to_lab(self.src_pixels_with_freq[i][0])

            # Check print first 10
            # for i in range(10):
            #     print(self.src_pixels_with_freq[i])

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
                        self.result_img_path = self.visualize_results(src_image_array, img.mode, img_width, img_height,
                                                                      run_num, k)
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

            # Get total time elapsed including file loading and conversion
            run_stop_time = perf_counter()
            self.total_time = run_stop_time - run_start_time

            # Log total time elapsed for this suite of runs
            logger.log(f"Summary: \nNumber of runs: {self.num_runs}\n"
                       f"k_start: {k_start}; k_end: {k_end}; k_interval: {k_interval}\n"
                       f"Total time elapsed (including file processing): {self.total_time} seconds.")

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

        # Get initial k colors via k-means++ selection
        kmpp_start_time = perf_counter()
        self.run_k_means_plus_plus(k)
        kmpp_stop_time = perf_counter()
        logger.log(f"Time elapsed for k-means++: {kmpp_stop_time - kmpp_start_time} seconds")

        # Print and log initial k_colors (now in LAB space!)
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
            # k_means_utils.group_pixels(self.src_pixels_with_coords, self.k_colors, self.k_clusters)
            k_means_utils.group_pixels(self.src_pixels_with_freq, self.k_colors, self.k_clusters)

            # Update k_colors by getting new representative color from each cluster,
            ## where the representative color is the average color by RGB values
            self.k_colors = k_means_utils.update_k_colors(self.k_clusters)

            # Update size of each cluster by counting sum of occurrences for each pixel
            self.k_clusters_sizes = []  # Wipe old sizes first
            for i in range(len(self.k_clusters)):
                size = 0
                curr_cluster = self.k_clusters[i]
                for j in range(len(curr_cluster)):
                    size += curr_cluster[j][1]
                self.k_clusters_sizes.append(size)

            # Log updated k_colors with iteration number
            iteration_num += 1
            logger.log("[ " + str(iteration_num) + "]: " + k_means_utils.stringify_tuple_list(self.k_colors))

            # Compare updated result with past result and update change boolean as needed
            result_changed = not k_means_utils.compare_tuple_lists(self.k_colors, last_k_colors)

        # Convert final k_colors back to RGB
        for i in range(len(self.k_colors)):
            self.k_colors[i] = k_means_utils.lab_to_rgb(self.k_colors[i])

        # Print and log resulting k_colors
        print("Representative k_colors: ", self.k_colors)
        logger.log("\nRepresentative k_colors: ")
        logger.log(k_means_utils.stringify_tuple_list(self.k_colors) + '\n')

        # Use perf counter for end time and log time elapsed
        stop_time = perf_counter()
        time_elapsed = stop_time - start_time
        # self.total_time += time_elapsed
        logger.log("Time elapsed for k-means algorithm: " + str(time_elapsed) + " seconds\n")

    ## Function to update self.k_colors with k initial centroids using k-means++
    # @param k - int value of k for current run
    #
    def run_k_means_plus_plus(self, k):
        print(f"Running k_means++ to select {k} centroids\n")
        # Initially select one pixel at random
        # NB choices returns list of 1 item by default, use [0] to access pixel, [0] again to access its LAB tuple
        self.k_colors.append(choices(self.src_pixels_with_freq)[0][0])
        # Create list of weights proportional to sq dist of each pixel to nearest selected center
        weights = []
        for i in range(len(self.src_pixels_with_freq)):
            curr_pixel = self.src_pixels_with_freq[i][0]
            curr_freq = self.src_pixels_with_freq[i][1]
            # Multiply weight of 1 color by its number of occurrences
            weights.append(k_means_utils.get_weight(self.k_colors, curr_pixel) * curr_freq)

        # While not k have been chosen:
        while len(self.k_colors) < k:
            # Choose next center
            self.k_colors.append(choices(self.src_pixels_with_freq, weights=weights)[0][0])
            # Update weights again
            for i in range(len(self.src_pixels_with_freq)):
                curr_pixel = self.src_pixels_with_freq[i][0]
                curr_freq = self.src_pixels_with_freq[i][1]
                # Update weight
                weights[i] = k_means_utils.get_weight(self.k_colors, curr_pixel) * curr_freq

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
                                                            self.k_colors, self.k_clusters_sizes)
        palette_img.save(palette_img_path)
        palette_img.close()

        # Create copy of original with pixels replaced by representative colors
        # if self.palette_replace:
        #     reduced_image_path = (f"./results/{k_means_utils.get_timestamp_str()}__{self.project_name}_[r]_run_"
        #                           f"{run_num + 1}_k_{k}{self.img_extension}")
        #     reduced_image = palette_utils.create_reduced_image(mode, img_width, img_height,
        #                                                        self.k_clusters, self.k_colors)
        #     reduced_image.save(reduced_image_path)
        #     reduced_image.close()

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
