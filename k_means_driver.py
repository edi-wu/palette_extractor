## Name: Eddie Wu
## Description: Driver file for running k-means

import cProfile
from K_Means import K_Means
import os


def main():
    # Prompt user for project name and image file path
    # src_images/img.jpeg
    relative_path = input("Enter file path relative to current directory: ")
    file_path = os.path.join(os.getcwd(), relative_path)
    project_name = input("Enter project or image name: ")

    # Prompt user for k values: either single value or ranged
    k_start, k_end, k_interval = -1, -1, 1
    print("Choose an option for k values: ")
    k_option = input("[S]ingle value\t[R]anged values: ")
    if k_option.upper() == "S":
        k_start = int(input("Enter the value for k: "))
        k_end = k_start
    elif k_option.upper() == "R":
        k_start = int(input("Enter the lower bound value for k: "))
        k_end = int(input("Enter the upper bound value for k: "))
        k_interval = int(input("Enter the k value increment interval: "))
    # Put together tuple representing k values
    k_values = (k_start, k_end, k_interval)

    # Prompt user for number of runs
    num_runs = int(input("Enter the number of runs using the specified k value(s): "))

    k_means_process = K_Means(project_name, k_values, file_path, num_runs)
    k_means_process.run()


if __name__ == "__main__":
    cProfile.run('main()')
