import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.app import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("trs")
    app.setApplicationDisplayName("trs — Transcribe Videos")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
