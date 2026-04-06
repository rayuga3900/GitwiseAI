import logging
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
 
# Python’s logging module needs to be configured once at the start to define how all logging messages behave throughout your program.
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s",
        handlers=[
            logging.StreamHandler(),           # console
            logging.FileHandler("app.log")     # file
        ]
    )