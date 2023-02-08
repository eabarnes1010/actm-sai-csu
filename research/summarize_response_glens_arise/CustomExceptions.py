''' CustomExceptions
Custom exceptions used within the SAI-CESM package.

Written by Daniel Hueholt
Graduate Research Assistant at Colorado State University
'''
class Error(Exception):
    '''Base class for exceptions in this module.'''
    pass

class NoDataError(Error):
    '''Exception raised when no data is found.
    Attributes:
        message -- explanation of the error
    '''

    def __init__(self, message):
        self.message = message
