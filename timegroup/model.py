import yaml
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import QObject, Slot, Signal, Property, QThread
from loguru import logger
from timegroup.utils.datetime_utils import get_time_frame
from timegroup.report import (
    Report, POSReport, RemainProductReport, AwaitingOrderReport,
    GHTKOrderReport, VTPOrderReport
)
from timegroup.utils.pancake_utils import request_shop_orders, request_product_variations
from timegroup.config import config

class ReportWorker(QObject):
    """This class performs the long-running report generation."""
    finished = Signal()
    progress = Signal(str)

    def __init__(self, report_type, time_frame):
        super().__init__()
        self.output_dir = os.path.expanduser("~/Downloads")
        self.report_type = report_type
        self.time_frame = time_frame

    def build_report_name(self, shop_name, report_type, time_frame):
        timestamp = datetime.now().strftime("%d%m%Y")
        report_file = f"{shop_name}-{self.report_type.replace(' ', '_').lower()}-{self.time_frame.replace(' ', '_').lower()}-{timestamp}.xlsx"
        report_path = os.path.join(self.output_dir, report_file)
        return report_path

    def run(self):
        logger.debug(f"Exporting report: {self.report_type} for {self.time_frame}")
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

            for shop_code, shop_data in shops.items():
                shop_id = shop_data["id"]
                shop_name = shop_data["name"]
                api_key = shop_data["api_key"]
                self.progress.emit(f"Đang xử lý {shop_name}...")

                # credentials = {"shop_id": shop_id, "api_key": api_key}
                start_date, end_date = get_time_frame(self.time_frame)
                logger.debug(f"Start date: {start_date}")
                logger.debug(f"End date: {end_date}")

                self.progress.emit(f"Đang lấy dữ liệu đơn hàng {shop_name}...")
                params = {
                    "updateStatus": 1,  # da_xac_nhan
                    "startDateTime": start_date,
                    "endDateTime": end_date,
                    "page_size": 100
                }
                # orders_data would be used for POS and CHỜ HÀNG
                orders_data = request_shop_orders(shop_id, params, api_key)

                # POS
                self.progress.emit(f"Đang tạo báo cáo POS cho {shop_name}...")
                pos_report = POSReport()
                pos_report.parse(orders_data)

                # CHO HANG
                self.progress.emit(f"Đang tạo báo cáo CHỜ HÀNG cho {shop_name}...")
                awaiting_order_report = AwaitingOrderReport()
                awaiting_order_report.parse(orders_data)

                # TON KHO
                self.progress.emit(f"Đang lấy dữ liệu tồn kho của {shop_name}...")
                params = {
                    "startDateTime": start_date,
                    "endDateTime": end_date,
                    "page_size": 100
                }
                product_data = request_product_variations(shop_id, params, api_key)
                self.progress.emit(f"Đang tạo báo cáo TỒN KHO {shop_name}...")
                remain_product_report = RemainProductReport()
                remain_product_report.parse(product_data)

                params = {
                    "updateStatus": "partner_inserted_at",  # day don sang DVVC
                    "startDateTime": start_date,
                    "endDateTime": end_date,
                    "page_size": 100
                }
                # orders_data would be used for POS and CHỜ HÀNG
                orders_data = request_shop_orders(shop_id, params, api_key)

                # Don hang GHTK
                self.progress.emit(f"Đang tạo báo cáo Đơn hàng GHTK {shop_name}...")
                ghtk_report = GHTKOrderReport()
                ghtk_report.parse(orders_data)

                # Don hang VTP
                self.progress.emit(f"Đang tạo báo cáo Đơn hàng VTP {shop_name}...")
                vtp_report = VTPOrderReport()
                vtp_report.parse(orders_data)

                # Merge all reports
                report = Report.merge(
                    pos_report,
                    remain_product_report,
                    awaiting_order_report,
                    ghtk_report,
                    vtp_report,
                )
                report_path = self.build_report_name(shop_name, self.report_type, self.time_frame)
                report.save(report_path)

            self.progress.emit(f"Hoàn thành!")
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
