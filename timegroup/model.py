import os
import shutil
import yaml
import sys
from collections import OrderedDict

from PySide6.QtCore import QObject, Slot, Signal, Property, QThread
from loguru import logger

from timegroup.utils.datetime_utils import get_time_frame
from timegroup.report import (
    SpreadSheet, POSReport, RemainProductReport, AwaitingOrderReport,
    GHTKOrderReport, VTPOrderReport
)
from timegroup.utils.pancake_utils import request_shop_orders, request_product_variations

class ModelConfig(QObject):
    def __init__(self, config_path):
        super().__init__()
        self._config_path = self._get_config_path(config_path)
        logger.debug(f"Config file: {self._config_path}")
        self._config = self._load(self._config_path)

    def _get_config_path(self, original_config_path):
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running in a normal Python environment
            base_path = os.path.dirname(os.path.abspath(__file__))

        config_file = os.path.basename(original_config_path)

        if sys.platform == 'win32':
            # On Windows, use LOCALAPPDATA
            app_data = os.environ.get('LOCALAPPDATA')
            if app_data:
                dest_dir = os.path.join(app_data, 'TimeGroup')
            else:
                # Fallback to temp directory if LOCALAPPDATA is not available
                dest_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'TimeGroup')
        else:
            # On Unix-like systems, use ~/.config
            dest_dir = os.path.join(os.path.expanduser('~'), '.config', 'timegroup')

        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, config_file)

        if not os.path.exists(dest_path):
            shutil.copy(os.path.join(base_path, original_config_path), dest_path)

        return dest_path

    def _load(self, config_file):
        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    @Slot(str, result="QVariant")
    def getValue(self, key):
        keys = key.split(".")
        config = self._config
        for k in keys:
            config = config.get(k)
            if config is None:
                return None
        return config

    @Slot(str, str)
    def setValue(self, key, value):
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = OrderedDict()
            config = config[k]
        config[keys[-1]] = value

    @Slot()
    def save(self):
        """Save the configuration back to the file with order preserved."""
        with open(self._config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

class ReportWorker(QObject):
    """Performs long-running report generation."""
    finished = Signal()
    progress = Signal(str)

    def __init__(self, report_type, spreadsheet_ids, time_frame, selected_reports):
        super().__init__()
        from timegroup.config import load_config
        self.config = load_config()
        self.report_type = report_type
        self.spreadsheet_ids = spreadsheet_ids
        self.time_frame = time_frame
        self.selected_reports = selected_reports

    def run(self):
        logger.debug(f"Exporting report: {self.report_type} for {self.time_frame}")
        self.progress.emit("Đang xử lý...")

        if self.report_type == "revenue":
            self._generate_revenue_report()
        elif self.report_type == "order":
            self._generate_order_report()

        self.progress.emit("Hoàn thành!")
        self.finished.emit()

    def _generate_revenue_report(self):
        shops = self.config["shops"]
        reports_info = self.config["reports"]

        for shop_code, shop_data in shops.items():
            self._process_shop_revenue(shop_code, shop_data, reports_info)

    def _generate_order_report(self):
        shops = self.config["shops"]
        reports_info = self.config["reports"]

        for shop_code, shop_data in shops.items():
            self._process_shop_order(shop_code, shop_data, reports_info)

    def _process_shop_revenue(self, shop_code, shop_data, reports_info):
        shop_id, shop_name, api_key = shop_data["id"], shop_data["name"], shop_data["api_key"]
        report_gid = reports_info["revenue"]["gid"]

        self.progress.emit(f"Đang xử lý {shop_name}...")
        start_date, end_date = get_time_frame(self.time_frame)

        reports = []

        if "Đơn hàng data" in self.selected_reports or "Chờ hàng + TỒN KHO" in self.selected_reports:
            orders_data = self._fetch_orders_data(shop_id, api_key, start_date, end_date, "Đang lấy dữ liệu đơn hàng")

            if "Đơn hàng data" in self.selected_reports:
                reports.append(self._create_pos_report(reports_info["revenue"]["don_hang"], orders_data, name="Đơn hàng data"))

            if "Chờ hàng + TỒN KHO" in self.selected_reports:
                reports.extend(self._create_awaiting_and_remain_reports(reports_info["revenue"]["cho_hang_ton_kho"], orders_data, shop_id, api_key, start_date, end_date))

        if "Khu vực data" in self.selected_reports:
            reports.extend(self._create_area_reports(reports_info["revenue"]["khu_vuc"], shop_id, api_key, start_date, end_date))

        self.progress.emit("Đang cập nhật dữ liệu vào spreadsheet...")
        self._upload_reports(report_gid, reports)

    def _process_shop_order(self, shop_code, shop_data, reports_info):
        shop_id, shop_name, api_key = shop_data["id"], shop_data["name"], shop_data["api_key"]
        report_gid = reports_info["order"][shop_code]["gid"]

        self.progress.emit(f"Đang xử lý {shop_name}...")
        start_date, end_date = get_time_frame(self.time_frame)

        reports = []

        if "CHỜ HÀNG" in self.selected_reports or "Pos" in self.selected_reports:
            orders_data = self._fetch_orders_data(shop_id, api_key, start_date, end_date, "Đang lấy dữ liệu đơn hàng")

            if "Pos data" in self.selected_reports:
                reports.append(self._create_pos_report(reports_info["order"]["pos"], orders_data))

            if "CHỜ HÀNG" in self.selected_reports:
                reports.append(self._create_awaiting_order_report(reports_info["order"]["cho_hang"], orders_data))

        if "TỒN KHO" in self.selected_reports:
            reports.append(self._create_remain_product_report(reports_info["order"]["ton_kho"], shop_id, api_key, start_date, end_date))

        if "Đơn hàng ghtk data" in self.selected_reports or "Đơn hàng vtp data" in self.selected_reports:
            delivery_orders_data = self._fetch_delivery_orders_data(shop_id, api_key, start_date, end_date, "Đang lấy dữ đẩy đẩy sang ĐVVC")

            if "Đơn hàng ghtk data" in self.selected_reports:
                reports.append(self._create_ghtk_report(reports_info["order"]["don_hang_ghtk"], delivery_orders_data))

            if "Đơn hàng vtp data" in self.selected_reports:
                reports.append(self._create_vtp_report(reports_info["order"]["don_hang_vtp"], delivery_orders_data))

        self._upload_reports(report_gid, reports)

    def _fetch_orders_data(self, shop_id, api_key, start_date, end_date, message=""):
        params = {
            "updateStatus": 1,  # da_xac_nhan
            "startDateTime": start_date,
            "endDateTime": end_date,
            "page_size": 100
        }
        return request_shop_orders(shop_id, params, api_key, progress_callback=lambda x: self.progress.emit(f"{message}. {x}"))

    def _fetch_delivery_orders_data(self, shop_id, api_key, start_date, end_date, message=""):
        params = {
            "updateStatus": "partner_inserted_at",  # day don sang DVVC
            "startDateTime": start_date,
            "endDateTime": end_date,
            "page_size": 100
        }
        return request_shop_orders(shop_id, params, api_key, progress_callback=lambda x: self.progress.emit(f"{message}. {x}"))

    def _create_pos_report(self, report_info, orders_data, name="Pos data"):
        self.progress.emit("Đang tạo báo cáo Đơn hàng/Pos...")
        pos_report = POSReport(name=name)
        pos_report.range_name = report_info["range_name"]
        pos_report.update_policy = report_info["policy"]
        pos_report.parse(orders_data)
        pos_report.reorder_columns([2, 3, 4, 5, 1, 0])
        return pos_report

    def _create_awaiting_and_remain_reports(self, report_info, orders_data, shop_id, api_key, start_date, end_date):
        self.progress.emit("Đang tạo báo cáo CHỜ HÀNG+TỒN KHO...")

        awaiting_report = AwaitingOrderReport(name="Chờ hàng + TỒN KHO")
        awaiting_report.range_name = report_info["range_name"][0]
        awaiting_report.update_policy = report_info["policy"][0]
        awaiting_report.parse(orders_data)

        self.progress.emit("Đang lấy dữ liệu TỒN KHO...")
        product_data = request_product_variations(shop_id, {"startDateTime": start_date, "endDateTime": end_date, "page_size": 100}, api_key)
        remain_report = RemainProductReport(name="Chờ hàng + TỒN KHO")
        remain_report.range_name = report_info["range_name"][1]
        remain_report.update_policy = report_info["policy"][1]
        remain_report.parse(product_data)

        return [awaiting_report, remain_report]

    def _create_area_reports(self, report_info, shop_id, api_key, start_date, end_date):
        orders_data = self._fetch_delivery_orders_data(shop_id, api_key, start_date, end_date)

        self.progress.emit("Đang tạo báo cáo Đơn hàng GHTK...")
        ghtk_report = GHTKOrderReport(name="Khu vực data")
        ghtk_report.range_name = report_info["range_name"][0]
        ghtk_report.parse(orders_data)
        ghtk_report.keep_columns([0, 14, 13, 16])

        self.progress.emit("Đang tạo báo cáo Đơn hàng VTP...")
        vtp_report = VTPOrderReport(name="Khu vực data")
        vtp_report.range_name = report_info["range_name"][1]
        vtp_report.parse(orders_data)
        vtp_report.keep_columns([0, 14, 13, 16])

        return [ghtk_report, vtp_report]

    def _create_awaiting_order_report(self, report_info, orders_data):
        self.progress.emit("Đang tạo báo cáo CHỜ HÀNG...")
        awaiting_report = AwaitingOrderReport()
        awaiting_report.range_name = report_info["range_name"]
        awaiting_report.update_policy = report_info["policy"]
        awaiting_report.parse(orders_data)
        return awaiting_report

    def _create_remain_product_report(self, report_info, shop_id, api_key, start_date, end_date):
        self.progress.emit("Đang lấy dữ liệu tồn kho...")
        product_data = request_product_variations(shop_id, {"startDateTime": start_date, "endDateTime": end_date, "page_size": 100}, api_key)
        self.progress.emit("Đang tạo báo cáo TỒN KHO...")
        remain_report = RemainProductReport()
        remain_report.range_name = report_info["range_name"]
        remain_report.update_policy = report_info["policy"]
        remain_report.parse(product_data)
        return remain_report

    def _create_ghtk_report(self, report_info, orders_data):
        self.progress.emit("Đang tạo báo cáo Đơn hàng GHTK...")
        ghtk_report = GHTKOrderReport()
        ghtk_report.range_name = report_info["range_name"]
        ghtk_report.update_policy = report_info["policy"]
        ghtk_report.parse(orders_data)
        return ghtk_report

    def _create_vtp_report(self, report_info, orders_data):
        self.progress.emit("Đang tạo báo cáo Đơn hàng VTP...")
        vtp_report = VTPOrderReport()
        vtp_report.range_name = report_info["range_name"]
        vtp_report.update_policy = report_info["policy"]
        vtp_report.parse(orders_data)
        return vtp_report

    def _upload_reports(self, report_gid, reports):
        spreadsheet = None
        try:
            spreadsheet = SpreadSheet(report_gid, reports)
            spreadsheet.upload()
        except Exception as e:
            self.progress.emit(f"Failed to upload data: {e}")
            logger.error(f"Failed to upload data: {e}")
            if spreadsheet:
                spreadsheet.rollback()

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

    @Slot(str, list, str, str)
    def exportReport(self, report_type, spreadsheet_ids, time_frame, selected_reports):
        self.log("inside exportReport")
        self.log(str(self.isExporting))
        if not self.isExporting:
            self.setIsExporting(True)
            self.setMessageInfo("Bắt đầu xuất báo cáo...")

            self.thread = QThread()
            self.worker = ReportWorker(report_type, spreadsheet_ids, time_frame, selected_reports)

            self.worker.moveToThread(self.thread)

            self.worker.progress.connect(self.setMessageInfo)
            self.worker.finished.connect(self.onReportFinished)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

    @Slot()
    def onReportFinished(self):
        self.setIsExporting(False)
        self.reportGenerated.emit("Report generation completed!")

    @Slot(str, str)
    def log(self, message, level="info"):
        if level == "info":
            logger.info(message)
        elif level == "debug":
            logger.debug(message)
        elif level == "error":
            logger.error(message)
        else:
            logger.info(message)
