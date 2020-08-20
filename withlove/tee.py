import os
import sys

class Tee(object):
    '''
    Tee - a very simple way to Tee output to both sys.stdout and a file
    Basis of some very simple logging that captures anything output via print()

    See start_simpler_logger for more information
    '''
    # TODO: may allow Tee to append to other media like messaging via socket
    def __init__(self, filename='Tee.txt',fileoption='w+',append=False):
        # If Tee exists, we can append or reset to a 2-way
        if isinstance(sys.stdout, Tee):
            if not append:
                # Not appending means rolling back (unstacking) on level
                # for the previous console object
                sys.stdout.file.close()
                sys.stdout = sys.stdout.console
        
        self.console = sys.stdout

        try:
            self.file = open(filename, fileoption)
        except Exception as e:
            self.file = None
            print(f'{filename} : FAILED TO OPEN : {repr(e)}')

    def write(self,message):
        self.console.write(message)
        try:
            self.console.flush() # Keep user up to day (avoid display latencies if possible)
        except:
            pass # Some redirects don't have flush, move along

        if self.file is not None:
            self.file.write(message)

    def flush(self):
        # For compatibility pass the console flush down until the real
        # console is invoked; this may happen if the user forked (appended)
        # Tee. In the future this might be important because we may allow
        # a 3-way or more to multiple destinations (like messages via sockets, etc)
        if isinstance(self.console, Tee):
            self.console.console.flush()


def start_simple_logging(module_file_name):
    ''' start_simple_logging - the simplest way to log everything output
    from calls to print

    USAGE:

        # Start recording everything sent to stdout and stderr to the current
        # working directory using the current module file name as the basis
        #
        # E.g., suppose you write a blah.py file and include the following

        import tee

        Tee.start_simple_logging(__file__)

        # The value of __file__ will be <path>/blah.py
        # This will create blah.txt in the current directory

        # change working directory before starting the logging if you want
        # to record to a different directory
    '''
    file_name = os.path.basename(module_file_name)
    module_name = os.path.splitext(file_name)[0]

    logfile_name = os.path.join('.', module_name + '.txt')
    sys.stdout = Tee(logfile_name)
    sys.stderr = sys.stdout

    return sys.stdout
    