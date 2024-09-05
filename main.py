import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from model import ReportModel
import rc_icons
import rc_main

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Determine the path to the icon
    if getattr(sys, 'frozen', False):
        # If running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # If running in a regular Python environment
        base_path = Path(__file__).resolve().parent

    icon_path = str(base_path / "resources/icons/timegroup.ico")
    app.setWindowIcon(QIcon(icon_path))
    engine = QQmlApplicationEngine()

    model = ReportModel()
    engine.rootContext().setContextProperty("reportModel", model)

    qml_file = "qrc:/qml/app.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
