# File: main.py
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QIODevice

from pathlib import Path

app = QApplication(sys.argv)

ui_file_name = Path(__file__).parent / "main_window.ui"
ui_file = QFile(str(ui_file_name))
if not ui_file.open(QIODevice.ReadOnly):
    print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
    sys.exit(-1)
loader = QUiLoader()
window = loader.load(ui_file)
ui_file.close()
if not window:
    print(loader.errorString())
    sys.exit(-1)
window.show()

sys.exit(app.exec_())