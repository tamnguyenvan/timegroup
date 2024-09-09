import yaml
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import QObject, Slot, Signal, Property, QThread
from loguru import logger
from timegroup.utils.datetime_utils import get_time_frame
from timegroup.report import (
    SpreadSheet, POSReport, RemainProductReport, AwaitingOrderReport,
    GHTKOrderReport, VTPOrderReport
)
from timegroup.utils.pancake_utils import request_shop_orders, request_product_variations
from timegroup.config import config

class ReportWorker(QObject):
    """This class performs the long-running report generation."""
    finished = Signal()
    progress = Signal(str)

    def __init__(self, report_type, time_frame, selected_reports):
        super().__init__()
        self.output_dir = os.path.expanduser("~/Downloads")
        self.report_type = report_type
        self.time_frame = time_frame
        self.selected_reports = selected_reports

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

                start_date, end_date = get_time_frame(self.time_frame)
                logger.debug(f"Start date: {start_date}")
                logger.debug(f"End date: {end_date}")

                reports = []

                if (
                    "CHỜ HÀNG" in self.selected_reports
                ):
                    pass

        elif self.report_type == "order":
            shops = config["shops"]
            reports_info = config["reports"]

            for shop_code, shop_data in shops.items():
                print(shop_code)
                shop_id = shop_data["id"]
                shop_name = shop_data["name"]
                api_key = shop_data["api_key"]
                report_gid = reports_info[shop_code]

                self.progress.emit(f"Đang xử lý {shop_name}...")

                start_date, end_date = get_time_frame(self.time_frame)
                logger.debug(f"Start date: {start_date}")
                logger.debug(f"End date: {end_date}")

                reports = []

                if (
                    "CHỜ HÀNG" in self.selected_reports
                    or "Pos" in self.selected_reports
                ):
                    print('pos, cho hang')
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
                    reports.append(pos_report)

                    # CHO HANG
                    self.progress.emit(f"Đang tạo báo cáo CHỜ HÀNG cho {shop_name}...")
                    awaiting_order_report = AwaitingOrderReport()
                    awaiting_order_report.parse(orders_data)
                    reports.append(awaiting_order_report)

                if "TỒN KHO" in self.selected_reports:
                    print('ton kho')
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
                    reports.append(remain_product_report)

                if (
                    "Đơn hàng ghtk" in self.selected_reports
                    or "Đơn hàng vtp" in self.selected_reports
                ):
                    print('don hang')
                    params = {
                        "updateStatus": "partner_inserted_at",  # day don sang DVVC
                        "startDateTime": start_date,
                        "endDateTime": end_date,
                        "page_size": 100
                    }
                    # orders_data would be used for and CHỜ HÀNG
                    orders_data = request_shop_orders(shop_id, params, api_key)

                    # Don hang GHTK
                    self.progress.emit(f"Đang tạo báo cáo Đơn hàng GHTK {shop_name}...")
                    ghtk_report = GHTKOrderReport()
                    ghtk_report.parse(orders_data)
                    reports.append(ghtk_report)

                    # Don hang VTP
                    self.progress.emit(f"Đang tạo báo cáo Đơn hàng VTP {shop_name}...")
                    vtp_report = VTPOrderReport()
                    vtp_report.parse(orders_data)
                    reports.append(vtp_report)

                # try:
                spreadsheet = SpreadSheet(report_gid, reports)
                spreadsheet.upload()
                # except Exception as e:
                #     logger.error(f"Failed to upload data shop {shop_id} gid {report_gid}: {e}")
                #     spreadsheet.rollback()

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

    @Slot(str, str, str)
    def exportReport(self, report_type, time_frame, selected_reports):
        if not self.isExporting:
            self.setIsExporting(True)
            self.setMessageInfo("Bắt đầu xuất báo cáo...")

            # Create a QThread and a worker
            self.thread = QThread()
            self.worker = ReportWorker(report_type, time_frame, selected_reports)

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
