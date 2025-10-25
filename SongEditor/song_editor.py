#! /usr/bin/env python3

import os
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow

def main():
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
