import yaml
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import QObject, Slot, Signal, Property, QThread
from loguru import logger
from timegroup.utils.datetime_utils import get_time_frame
from timegroup.report import request_orders_data, write_order_report


def load_config(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).resolve().parent

config_path = os.path.join(base_path, "config.yaml")
config = load_config(config_path)


class ReportWorker(QObject):
    """This class performs the long-running report generation."""
    finished = Signal()
    progress = Signal(str)

    def __init__(self, report_type, time_frame):
        super().__init__()
        self.output_dir = os.path.expanduser("~/Downloads")
        self.report_type = report_type
        self.time_frame = time_frame

    def run(self):
        logger.debug(f"Exporting report: {self.report_type} for {self.time_frame}")
        timestamp = datetime.now().strftime("%d%m%Y")
        report_file = f"{self.report_type.replace(' ', '_').lower()}-{self.time_frame.replace(' ', '_').lower()}-{timestamp}.xlsx"
        report_path = os.path.join(self.output_dir, report_file)
        self.progress.emit("Đang xử lý...")

        if self.report_type == "revenue":
            shops = config["shops"]
            for shop_code, shop_data in shops.items():
                shop_id = shop_data["id"]
                shop_name = shop_data["name"]
                api_key = shop_data["api_key"]
                self.progress.emit(f"Đang xử lý {shop_name}...")

                credentials = {"shop_id": shop_id, "api_key": api_key}
                # create_revenue_report(credentials, self.time_frame, report_path)
        elif self.report_type == "order":
            shops = config["shops"]
            aggregated_orders_data = []
            for shop_code, shop_data in shops.items():
                shop_id = shop_data["id"]
                shop_name = shop_data["name"]
                api_key = shop_data["api_key"]
                self.progress.emit(f"Đang xử lý {shop_name}...")

                credentials = {"shop_id": shop_id, "api_key": api_key}
                start_date, end_date = get_time_frame(self.time_frame)
                logger.debug(f"Start date: {start_date}")
                logger.debug(f"End date: {end_date}")
                orders_data = request_orders_data(credentials, start_date, end_date)
                aggregated_orders_data += orders_data

            write_order_report(report_path, aggregated_orders_data)

        self.progress.emit(f"Hoàn thành! ~/Downloads/{report_file}")
        self.finished.emit()


class ReportModel(QObject):
    reportGenerated = Signal(str)
    isExportingChanged = Signal()
    messageInfoChanged = Signal()

    def __init__(self):
        super().__init__()
        self._isExporting = False
        self._messageInfo = ""

    @Property(bool, notify=isExportingChanged)
    def isExporting(self):
        return self._isExporting

    def setIsExporting(self, value):
        if self._isExporting != value:
            self._isExporting = value
            self.isExportingChanged.emit()

    @Property(str, notify=messageInfoChanged)
    def messageInfo(self):
        return self._messageInfo

    def setMessageInfo(self, value):
        if self._messageInfo != value:
            self._messageInfo = value
            self.messageInfoChanged.emit()

    @Slot(str, str)
    def exportReport(self, report_type, time_frame):
        if not self.isExporting:
            self.setIsExporting(True)
            self.setMessageInfo("Bắt đầu xuất báo cáo...")

            # Create a QThread and a worker
            self.thread = QThread()
            self.worker = ReportWorker(report_type, time_frame)

            # Move the worker to the thread
            self.worker.moveToThread(self.thread)

            # Connect signals
            self.worker.progress.connect(self.setMessageInfo)
            self.worker.finished.connect(self.onReportFinished)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            # Start the thread
            self.thread.start()

    @Slot()
    def onReportFinished(self):
        self.setIsExporting(False)
        self.reportGenerated.emit("Report generation completed!")
