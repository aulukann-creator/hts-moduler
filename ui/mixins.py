import os

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter


class WatermarkDialogMixin:
    """
    QDialog / QWidget türevlerinde arka plana merkezde şeffaf logo çizer.
    WatermarkBackground ile aynı mantık, ama dialoglar için bağımsız.
    """
    def init_watermark(self, logo_path=None, opacity=0.04, scale_ratio=0.85):

        base_dir = os.path.dirname(__file__)
        if logo_path is None:
            logo_path = os.path.join(base_dir, "assets", "bg_logo.png")
            if not os.path.exists(logo_path):
                logo_path = os.path.join(base_dir, "assets", "logo.png")

        self._bg_logo = QPixmap(logo_path)
        self._bg_logo_opacity = opacity
        self._bg_logo_scale_ratio = scale_ratio

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event):
        super().paintEvent(event)

        if not hasattr(self, "_bg_logo") or self._bg_logo.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = self.width(), self.height()
        target_w = int(w * self._bg_logo_scale_ratio)
        target_h = int(h * self._bg_logo_scale_ratio)

        scaled = self._bg_logo.scaled(
            QSize(target_w, target_h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        x = (w - scaled.width()) // 2
        y = (h - scaled.height()) // 2

        painter.setOpacity(self._bg_logo_opacity)
        painter.drawPixmap(x, y, scaled)
        painter.end()
