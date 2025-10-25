#! /usr/bin/env python3

import os
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow
from config import Config

def main():
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"
    Config.load("config.json")
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    e = app.exec()
    Config.save("config.json")
    sys.exit(e)

if __name__ == "__main__":
    main()
