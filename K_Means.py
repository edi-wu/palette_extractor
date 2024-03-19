## Name: Eddie Wu
## Description: Class for k-means process


from PIL import Image
from Logger import Logger
from time import perf_counter, ctime
import k_means_utils
import palette_utils


class K_Means:
    ## Constructor
    # @param project_name - string for name of project/image
    # @param k_values - tuple (start, end, interval) for number of clusters
    # @param file_path - file path for source image
    # @param num_runs - int number of runs for this image
    # @param log_file_name - string for the log file name
    # src_pixels: list of RGB tuples for all pixels in source image
    # k_colors: list of RGB tuples
    # k_clusters: list of lists, each list contains RGB tuples
    def __init__(self, project_name, k_values, file_path, num_runs, log_file_name):
        self.project_name = project_name
        self.file_path = file_path
        self.k_values = k_values
        self.num_runs = num_runs
        self.log_file_name = log_file_name

        self.src_pixels = []
        self.k_colors = []
        self.k_clusters = [[]]

    ## Main function to run k-means
    def run(self):
        print('\nPlease wait... running k-means clustering.')

        with Image.open(self.file_path) as img, Logger(self.log_file_name) as logger:

            logger.log('Project Name: ' + self.project_name + '\n\n')

            # Load image array
            src_image_array = img.load()
            img_height, img_width = img.height, img.width

            # Obtain list of pixels as RGB tuples
            for x in range(img_width):
                for y in range(img_height):
                    self.src_pixels.append(src_image_array[x, y])

            # Loop to run n times for specified values of k (single or ranged)
            k_start, k_end, k_interval = self.k_values
            for run_num in range(self.num_runs):
                logger.log(f"{'~' * 6} Run #{run_num + 1} of {self.num_runs} {'~' * 6}\n")
                for k in range(k_start, k_end + 1, k_interval):
                    logger.log("k = " + str(k))
                    # Initialize k_clusters based on current k value
                    self.k_clusters = [[] for _ in range(k)]
                    try:
                        # Run k-means algorithm
                        self.run_k_means(src_image_array, img_height, img_width, k, logger)
                        # Create result palette images
                        ## TODO: append palette to image; also do pixel replacements
                        palette_img_path = (f"./results/{self.project_name}_run_{run_num + 1}_k_{k}_"
                                            f"{ctime().replace(" ", "_")}.png")
                        palette_img = palette_utils.create_palette(self.k_colors)
                        palette_img.save(palette_img_path)
                    except Exception as e:
                        print('Quitting current run due to error: ' + str(e))
                        logger.log('Quitting current run due to error: ' + str(e))

            # Perform any necessary cleanup / analysis

    # Runs k-means clustering algorithm once
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

        # Get the initial k colors (list of pixel tuples) by randomly selecting coordinates
        ## Coordinates' max value is 1 less than dimension
        k_random_coords = k_means_utils.get_k_random_coords(k, w - 1, h - 1)
        self.k_colors = k_means_utils.map_coords_to_pixels(k_random_coords, src_image_array)

        # Print and log initial k_colors
        print("Initial k_colors (randomly selected): ", self.k_colors)
        logger.log("Initial k_colors (randomly selected): ")
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
            k_means_utils.group_pixels(self.src_pixels, self.k_colors, self.k_clusters)

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
        logger.log("Time elapsed: " + str(stop_time - start_time) + " seconds.\n")
