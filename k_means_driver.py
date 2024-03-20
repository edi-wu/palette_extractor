## Name: Eddie Wu
## Description: Driver file for running k-means

import cProfile
import os
import time
from K_Means import K_Means


def main():
    # Prompt user for project name and image file path
    # src_images/img.jpeg
    relative_path = input("Enter file path relative to current directory: ")
    file_path = os.path.join(os.getcwd(), relative_path)
    img_extension = f".{relative_path.rsplit(".", 1)[1]}"
    project_name = input("Enter project or image name: ")

    # Prompt user for k values: either single value or ranged
    k_start, k_end, k_interval = -1, -1, 1
    print("Choose an option for k values: ")
    k_option = input("[S]ingle value\t[R]anged values: ").upper()
    if k_option == "S":
        k_start = int(input("Enter the value for k: "))
        k_end = k_start
    elif k_option == "R":
        k_start = int(input("Enter the lower bound value for k: "))
        k_end = int(input("Enter the upper bound value for k: "))
        k_interval = int(input("Enter the k value increment interval: "))
    # Put together tuple representing k values
    k_values = (k_start, k_end, k_interval)

    # Prompt user for number of runs
    num_runs = int(input("Enter the number of runs using the specified k value(s): "))

    # Prompt user to choose whether to create result images that are pixel-replaced
    user_input = input("In addition to resulting palette, also create copy of original image"
                       " in which all pixels are replaced with their representative color? (Y/N): ")
    palette_replace = False
    if user_input.upper() == 'Y':
        palette_replace = True

    # Create the log file name based on above info
    log_file_name = f"{project_name}__{str(num_runs)}x_"
    if k_option == "S":
        log_file_name += f"({k_start})__"
    elif k_option == "R":
        log_file_name += f"({k_start}_{k_end}_{k_interval})__"
    log_file_name += time.ctime().replace(" ", "_")

    k_means_process = K_Means(project_name, k_values, file_path, num_runs, log_file_name, img_extension, palette_replace)
    k_means_process.run()


if __name__ == "__main__":
    cProfile.run('main()')
