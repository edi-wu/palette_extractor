## Name: Eddie Wu
## Date: 3/6/2024
## Description: Class to log data into text file

class Logger:
    ## Constructor
    # @param log_file_path - path for log file
    def __init__(self, log_file_name):
        self.log_file_path = "./logs/" + log_file_name
        self.file = None

    ## Enter method for context manager: opens file
    def __enter__(self):
        self.file = open(self.log_file_path, 'a')
        return self

    ## Method for writing a line into the log file
    # @param line - string for a single line
    def log(self, line):
        if self.file is not None:
            self.file.write(line + '\n')

    ## Exit method for context manager: closes file
    def __exit__(self, exception_type, exception_object, exception_traceback):
        if self.file is not None:
            self.file.close()
            self.file = None
