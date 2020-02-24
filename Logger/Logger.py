import logging

logging.basicConfig(level=logging.INFO)

logging.warning('Watch out!')  # will print a message to the console
logging.info('I told you so')  # will not print anything
logging.debug('Houston!')  # will print a message to the console
logging.critical("Dieing now.")
logging.error("Ouch")
