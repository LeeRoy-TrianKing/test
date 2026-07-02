from PySide6.QtGui import QPixmap, QPainter, QColor, QPolygonF, QPen
from PySide6.QtCore import QPointF, Qt, QRectF

def create_icon():
    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent) # 透明背景

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing) # 开启抗锯齿

    # 1. 绘制圆角方形背景 (使用你界面的主色调 #0066cc)
    painter.setBrush(QColor("#0066cc"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size, size, 50, 50)

    # 2. 绘制雷达波纹 (白色半透明弧线)
    pen = QPen(QColor(255, 255, 255, 180), 8) # 白色，透明度180，宽度8
    painter.setPen(pen)
    center_x, center_y = size / 2, size * 0.65

    # 画三层弧线
    for r in [40, 75, 110]:
        rect = QRectF(center_x - r, center_y - r, r * 2, r * 2)
        painter.drawArc(rect, 0 * 16, 180 * 16) # 画上半圆弧

    # 3. 绘制船只三角形 (纯白色)
    painter.setBrush(QColor("#ffffff"))
    painter.setPen(Qt.NoPen)

    # 三个顶点构成一个船头向上的三角形
    p1 = QPointF(size / 2, size * 0.2)          # 顶点
    p2 = QPointF(size * 0.62, size * 0.55)      # 右底
    p3 = QPointF(size * 0.38, size * 0.55)      # 左底
    triangle = QPolygonF([p1, p2, p3])
    painter.drawPolygon(triangle)

    painter.end()

    # 保存为 ico 文件
    pixmap.save("app.ico", "ICO")
    print("✅ 图标已生成: app.ico")

if __name__ == "__main__":
    create_icon()
