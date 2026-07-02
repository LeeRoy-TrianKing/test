import sys
import socket
import csv
import time
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QGridLayout, QLineEdit, QSpinBox,
                                QDoubleSpinBox, QComboBox, QPushButton, QTextEdit,
                                QGroupBox, QLabel, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from pyais.encode import encode_dict

# 现代化亮色主题 QSS 样式 (macOS / Fluent 风格)
LIGHT_THEME_STYLE = """
QMainWindow {
    background-color: #f5f5f7;
}
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e2e5;
    border-radius: 10px;
    margin-top: 18px;
    padding-top: 18px;
    color: #1d1d1f;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
    color: #0066cc;
    font-size: 14px;
}
QLabel {
    color: #424245;
}
QLabel#field_name {
    color: #1d1d1f;
    font-weight: bold;
    font-size: 13px;
}
QLabel#hint_label {
    color: #86868b;
    font-size: 12px;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #f5f5f7;
    color: #1d1d1f;
    border: 1px solid #d2d2d7;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 22px;
    selection-background-color: #0066cc;
    selection-color: white;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #0066cc;
    background-color: #ffffff;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1d1d1f;
    selection-background-color: #0066cc;
    selection-color: white;
    border: 1px solid #d2d2d7;
    border-radius: 4px;
}
QPushButton {
    background-color: #0066cc;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #0077ed;
}
QPushButton:pressed {
    background-color: #0055b3;
}
QPushButton#secondary_btn {
    background-color: #e5e5ea;
    color: #1d1d1f;
}
QPushButton#secondary_btn:hover {
    background-color: #d1d1d6;
}
QTextEdit {
    background-color: #ffffff;
    color: #1d1d1f;
    border: 1px solid #e2e2e5;
    border-radius: 8px;
    padding: 10px;
    font-family: 'Consolas', 'Menlo', 'Microsoft YaHei UI', monospace;
    font-size: 13px;
}
QScrollBar:vertical {
    border: none;
    background: #f5f5f7;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #c7c7cc;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #a8a8ad;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIS 消息类型 1 发送工具")
        self.resize(900, 750)
        self.setStyleSheet(LIGHT_THEME_STYLE)

        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ==================== 第一块：网络配置 ====================
        net_group = QGroupBox("网络配置")
        net_layout = QHBoxLayout(net_group)
        net_layout.setSpacing(15)

        self.ip_input = QLineEdit("127.0.0.1")
        self.ip_input.setFixedHeight(32)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(10110)
        self.port_input.setFixedHeight(32)

        net_layout.addWidget(QLabel("目标 IP:"))
        net_layout.addWidget(self.ip_input, 3)
        net_layout.addSpacing(20)
        net_layout.addWidget(QLabel("目标端口:"))
        net_layout.addWidget(self.port_input, 1)
        net_layout.addStretch()

        main_layout.addWidget(net_group)

        # ==================== 第二块：消息字段 ====================
        msg_group = QGroupBox("AIS 消息字段 (Type 1: A类位置报告)")
        msg_layout = QGridLayout(msg_group)
        msg_layout.setSpacing(12)
        msg_layout.setColumnStretch(0, 0)
        msg_layout.setColumnStretch(1, 0)
        msg_layout.setColumnStretch(2, 1)

        def add_field_row(row, name, widget, hint_text):
            name_label = QLabel(name)
            name_label.setObjectName("field_name")
            name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            hint_label = QLabel(hint_text)
            hint_label.setObjectName("hint_label")
            hint_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            hint_label.setWordWrap(True)

            widget.setFixedWidth(180)
            widget.setFixedHeight(32)

            msg_layout.addWidget(name_label, row, 0)
            msg_layout.addWidget(widget, row, 1)
            msg_layout.addWidget(hint_label, row, 2)

        # 1. Repeat
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItem("0: 首次发送")
        self.repeat_combo.addItem("1: 第2次转发")
        self.repeat_combo.addItem("2: 第3次转发")
        self.repeat_combo.addItem("3: 不再转发")
        add_field_row(0, "重复指示:", self.repeat_combo, "指示该消息被转发的次数。0表示首次发送，3表示已转发3次不再转发。")

        # 2. MMSI
        self.mmsi_input = QLineEdit("412345678")
        self.mmsi_input.setMaxLength(9)
        add_field_row(1, "MMSI:", self.mmsi_input, "海上移动业务识别码。9位纯数字，范围: 000000000 - 999999999。")

        # 3. Status
        self.status_combo = QComboBox()
        statuses = [
            ("0: 在动力下航行"), ("1: 锚泊"), ("2: 未受指令"), ("3: 受限制的机动能力"),
            ("4: 受吃水限制"), ("5: 系泊"), ("6: 搁浅"), ("7: 捕鱼中"),
            ("8: 航行中"), ("9: 被保留 (未来使用)"), ("10-14: 保留"), ("15: 未定义")
        ]
        for s in statuses:
            self.status_combo.addItem(s)
        self.status_combo.setCurrentIndex(1)
        add_field_row(2, "航海状态:", self.status_combo, "船舶当前动态。例如：1=锚泊，5=系泊，7=捕鱼中。")

        # 4. ROT
        self.rot_input = QDoubleSpinBox()
        self.rot_input.setRange(-127.0, 127.0)
        self.rot_input.setValue(0.0)
        add_field_row(3, "转弯率 (ROT):", self.rot_input, "对地转弯率。范围: -127 到 127。0=直行，正数=右转，负数=左转。")

        # 5. SOG
        self.sog_input = QDoubleSpinBox()
        self.sog_input.setRange(0.0, 102.2)
        self.sog_input.setValue(12.5)
        add_field_row(4, "对地航速 (节):", self.sog_input, "对地航速 (SOG)。范围: 0 到 102.2 节。")

        # 6. Accuracy
        self.acc_combo = QComboBox()
        self.acc_combo.addItem("0: 低精度 (>10m)")
        self.acc_combo.addItem("1: 高精度 (<10m)")
        add_field_row(5, "位置精度:", self.acc_combo, "GNSS位置精度。0=非差分(>10m)，1=差分高精度(<=10m)。")

        # 7. Longitude
        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180.0, 180.0)
        self.lon_input.setDecimals(4)
        self.lon_input.setValue(121.4737)
        add_field_row(6, "经度:", self.lon_input, "经度。范围: -180 到 180 度。东经为正，西经为负。")

        # 8. Latitude
        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90.0, 90.0)
        self.lat_input.setDecimals(4)
        self.lat_input.setValue(31.2304)
        add_field_row(7, "纬度:", self.lat_input, "纬度。范围: -90 到 90 度。北纬为正，南纬为负。")

        # 9. COG
        self.cog_input = QDoubleSpinBox()
        self.cog_input.setRange(0.0, 359.9)
        self.cog_input.setDecimals(1)
        self.cog_input.setValue(135.5)
        add_field_row(8, "对地航向 (度):", self.cog_input, "对地航向 (COG)。范围: 0 到 359.9 度。")

        # 10. Heading
        self.heading_input = QSpinBox()
        self.heading_input.setRange(0, 511)
        self.heading_input.setValue(136)
        add_field_row(9, "真实航向 (度):", self.heading_input, "真实船首向。范围: 0 到 359 度。511表示不可用。")

        # 11. UTC Second
        self.second_input = QSpinBox()
        self.second_input.setRange(0, 63)
        self.second_input.setValue(30)
        add_field_row(10, "UTC 秒:", self.second_input, "报告产生时的UTC秒数。0-59有效，60=不可用，61=手动，62=估算，63=无效。")

        # 12. RAIM
        self.raim_combo = QComboBox()
        self.raim_combo.addItem("0: 未使用 RAIM")
        self.raim_combo.addItem("1: 使用 RAIM")
        add_field_row(11, "RAIM 标志:", self.raim_combo, "接收机自主完好性监测。0=未使用，1=正在使用。")

        main_layout.addWidget(msg_group)

        # ==================== 按钮区域 ====================
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.send_btn = QPushButton("⬆  发送 AIS 消息")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setFixedHeight(40)
        self.send_btn.clicked.connect(self.send_message)

        self.import_btn = QPushButton("📂  导入 CSV 批量发送")
        self.import_btn.setObjectName("secondary_btn") # 次要按钮样式
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.setFixedHeight(40)
        self.import_btn.clicked.connect(self.import_csv_and_send)

        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.import_btn)
        main_layout.addLayout(btn_layout)

        # ==================== 第三块：日志框 ====================
        log_group = QGroupBox("发送日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("发送的 NMEA 语句将在此显示...")
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group)

    # ==================== 日志与核心发送逻辑 ====================

    def append_log(self, timestamp, nmea_str, is_error=False, is_info=False):
        """向日志框追加格式化的时间戳和NMEA字符串"""
        self.log_text.moveCursor(QTextCursor.End)

        if is_error:
            html = f'<span style="color: #ff3b30; font-weight: bold;">[{timestamp}] 错误: {nmea_str}</span><br>'
        elif is_info:
            html = f'<span style="color: #86868b;">[{timestamp}] {nmea_str}</span><br>'
        else:
            html = (f'<span style="color: #86868b;">[{timestamp}]</span> '
                    f'<span style="color: #0066cc; font-weight: bold;">{nmea_str}</span><br>')

        self.log_text.insertHtml(html)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def send_single_data(self, data_dict):
        """核心发送逻辑：接收一个包含AIS字段的字典，编码并通过UDP发送"""
        ip = self.ip_input.text().strip()
        port = self.port_input.value()

        try:
            # 生成 AIVDM 语句
            nmea_sentences = encode_dict(data_dict, radio_channel="B", talker_id="AI", sentence_type="VDM")

            # 创建 UDP Socket 并发送
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                for sentence in nmea_sentences:
                    payload = sentence.encode("ascii")
                    sock.sendto(payload, (ip, port))

                    # 获取当前时间戳并记录日志
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.append_log(now, sentence)
            finally:
                sock.close()

        except Exception as e:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.append_log(now, str(e), is_error=True)

    # ==================== 单条发送与 CSV 批量发送 ====================

    def send_message(self):
        """从界面获取数据并发送单条消息"""
        mmsi_str = self.mmsi_input.text().strip()
        if not mmsi_str.isdigit():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.append_log(now, "MMSI 必须为 9 位纯数字！", is_error=True)
            return

        status_val = int(self.status_combo.currentText().split(":")[0].split("-")[0])

        data = {
            'type': 1,
            'repeat': self.repeat_combo.currentIndex(),
            'mmsi': mmsi_str,
            'status': status_val,
            'rot': self.rot_input.value(),
            'sog': self.sog_input.value(),
            'accuracy': self.acc_combo.currentIndex(),
            'lon': self.lon_input.value(),
            'lat': self.lat_input.value(),
            'cog': self.cog_input.value(),
            'heading': self.heading_input.value(),
            'second': self.second_input.value(),
            'raim': self.raim_combo.currentIndex()
        }

        self.send_single_data(data)

    def import_csv_and_send(self):
        """打开文件对话框选择CSV，解析并循环发送"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 CSV 文件", "", "CSV Files (*.csv)")
        if not file_path:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_log(now, f"开始导入 CSV 文件: {file_path}", is_info=True)

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                # 使用 DictReader 方便按表头名读取
                reader = csv.DictReader(f)

                count = 0
                for row in reader:
                    try:
                        # 将 CSV 中的字符串转换为 pyais 需要的类型
                        data = {
                            'type': 1,
                            'repeat': int(row.get('repeat', 0)),
                            'mmsi': str(row.get('mmsi', '000000000')).strip(),
                            'status': int(row.get('status', 0)),
                            'rot': float(row.get('rot', 0)),
                            'sog': float(row.get('sog', 0)),
                            'accuracy': int(row.get('accuracy', 0)),
                            'lon': float(row.get('lon', 0)),
                            'lat': float(row.get('lat', 0)),
                            'cog': float(row.get('cog', 0)),
                            'heading': int(row.get('heading', 0)),
                            'second': int(row.get('second', 0)),
                            'raim': int(row.get('raim', 0))
                        }

                        # 调用核心发送逻辑
                        self.send_single_data(data)
                        count += 1

                        # 刷新界面并稍微延迟，防止阻塞UI和网络瞬间拥堵
                        QApplication.processEvents()
                        time.sleep(0.1)

                    except ValueError as ve:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.append_log(now, f"第 {count+2} 行数据格式错误，已跳过: {ve}", is_error=True)
                        continue

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.append_log(now, f"批量发送完毕，共发送 {count} 条数据。", is_info=True)

        except Exception as e:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.append_log(now, f"读取或发送 CSV 时发生错误: {str(e)}", is_error=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
