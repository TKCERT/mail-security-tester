# Reporting of test results

import csv

class DummyLogger:
    """/dev/null logger"""
    def __init__(self):
        pass

    def log(self, test : str, testid : int, recipient : str, delivered : bool = True, code : int = 0, msg : str = ""):
        pass

    def close(self):
        pass

class CSVLogger:
    """Logging of test results"""
    def __init__(self, logfile):
        self.csvfile = open(logfile, "w")
        self.csv = csv.writer(self.csvfile)
        self.csv.writerow(("Test Class", "Test ID", "Recipient", "Delivered", "Code", "Message"))

    def log(self, test : str, testid: int, recipient : str, delivered : bool = True, code : int = 0, msg : str = ""):
        """Log result"""
        self.csv.writerow((test, testid, recipient, delivered, code, msg))

    def close(self):
        self.csvfile.close()
