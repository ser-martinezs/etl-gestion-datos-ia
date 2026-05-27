import logging
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "logs"))


def get_process_logger(logger_name, filename):
	os.makedirs(LOG_DIR, exist_ok=True)
	logger = logging.getLogger(logger_name)
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	logger.propagate = False

	file_handler = logging.FileHandler(os.path.join(LOG_DIR, filename), encoding="utf-8")
	file_handler.setFormatter(
		logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
	)
	logger.addHandler(file_handler)
	return logger