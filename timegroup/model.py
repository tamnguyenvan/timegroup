import os
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal
import yaml


def load_config(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(config_file)
    return config

if getattr(sys, 'frozen', False):
    # If running in a PyInstaller bundle
    base_path = Path(sys._MEIPASS)
else:
    # If running in a regular Python environment
    base_path = Path(__file__).resolve().parent

config_path = os.path.join(base_path, "config.yaml")
config = load_config(config_path)

class ReportModel(QObject):
    reportGenerated = Signal(str)
    messageInfo = Signal(str)

    def __init__(self):
        super().__init__()

    @Slot(str, str)
    def exportReport(self, report_type, time_period):
        # Logic to export the report based on the type and time period
        print(f"Exporting report: {report_type} for {time_period}")

        report_file = f"{report_type.replace(' ', '_').lower()}_{time_period.replace(' ', '_').lower()}.xlsx"
        self.messageInfo.emit("Đang xử lý...")

        if report_type == "revenue":
            from timegroup.revenue_report import create_report
            shop_ids = config["shop_ids"]
            for shop_id in shop_ids:
                time_period = []
                create_report(shop_id, time_period)
        elif report_type == "order":
            pass
        else:
            ValueError("")

        # Emit signal when done
        self.reportGenerated.emit(report_file)