## Name: Eddie Wu
## Date: 2/20/2024
## Description: Functions for console UI menu with branching and validation

import os
import image_tools


## Presents main menu and calls appropriate functions based on user choice
#
def present_menu():
    # Constants for current directory, image options, and processing options
    DIRECTORY = os.getcwd()
    IMAGE_OPTIONS = ['laptop_photo.jpg', 'queen_mary.jpeg']
    PROCESSING_OPTIONS = ['Lighten/Darken', 'Channel Color', 'Invert Color', 'Add Blur', 'Detect Edges']

    # Variable for user choice
    user_choice = ''

    # Loop to run program until sentinel is detected
    while user_choice.upper() != 'Q':
        # Prompt user to choose image to alter
        print("\nChoose an image to alter, or Q to quit: ")

        # Print choices for image options
        for i in range(len(IMAGE_OPTIONS)):
            print(f"{i + 1}) {IMAGE_OPTIONS[i]}")
        user_choice = input()

        # Join to get full file path and save to variable
        file_path = os.path.join(DIRECTORY, IMAGE_OPTIONS[int(user_choice) - 1])

        # Exit loop if user chose to quit
        if user_choice.upper() == 'Q':
            break

        # Prompt user to choose processing option
        print("\nChoose a processing option, or Q to quit: ")

        # Print choices for processing
        for i in range(len(PROCESSING_OPTIONS)):
            print(f"{i + 1}) {PROCESSING_OPTIONS[i]}")
        user_choice = input()
        if user_choice.upper() == 'Q':
            break

        processing_option = int(user_choice)
        # Call appropriate processing function based on user choice
        ## Option 1: Lighten or darken
        if processing_option == 1:
            # Prompt user to choose lighten or darken
            ld_choice = ''
            while ld_choice.upper() != 'L' and ld_choice.upper() != 'D':
                ld_choice = input("Enter L for lighten or D for darken: ")
            # Prompt user to choose lighten or darken amount
            ld_amount = -1
            while ld_amount > 100 or ld_amount < 0:
                ld_amount = int(input("Enter an amount for processing between 0% and 100%: "))
            image_tools.process_image(file_path, processing_option, ld_option=ld_choice, amount=ld_amount)
        ## Option 2: Channel color
        elif processing_option == 2:
            # Prompt user to choose a color channel
            CHANNELS = set("RGB")
            channel_choice = ''
            while channel_choice.upper() not in CHANNELS:
                channel_choice = input("Enter color channel (R/G/B): ")
            image_tools.process_image(file_path, processing_option, channel=channel_choice)
        # Remaining options do not require additional arguments to the main processing function
        ## Option 3: Invert colors
        ## Option 4: Add blur
        ## Option 5: Detect edges
        else:
            image_tools.process_image(file_path, processing_option)

        # Prompt user to process another image or quit
        user_choice = input("\nProcess another image? (Y/N): ")
        if user_choice.upper() != 'Y':
            user_choice = 'Q'
