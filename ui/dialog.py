from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QPushButton, QWidget, QApplication

from ui.mixins import WatermarkDialogMixin


class ModernDialog(WatermarkDialogMixin, QDialog):
    """Hem Bilgi hem de Soru (Evet/Hayır) pencereleri için modern tasarım."""
    def __init__(self, parent, title, message, type="INFO", yes_text="Evet", no_text="Hayır"):
        super().__init__(parent)

        self.init_watermark(opacity=0.025, scale_ratio=0.85)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(420, 220)
        self.result_value = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)

        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(25, 20, 25, 20)

        color = "#3498db"
        icon_text = "ℹ️"

        if type == "ERROR":
            color = "#e74c3c"; icon_text = "❌"
        elif type == "SUCCESS":
            color = "#2ecc71"; icon_text = "✅"
        elif type == "WARNING":
            color = "#f39c12"; icon_text = "⚠️"
        elif type == "QUESTION":
            color = "#8e44ad"; icon_text = "❓"

        lbl_title = QLabel(f"{icon_text}  {title}")
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color}; border: none;")
        f_layout.addWidget(lbl_title)

        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet("font-size: 14px; color: #34495e; margin-top: 10px; margin-bottom: 20px; border: none;")
        f_layout.addWidget(lbl_msg)

        f_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        base_style = "QPushButton { font-weight: bold; padding: 8px 20px; border-radius: 6px; border: none; font-size: 13px; }"

        if type == "QUESTION":
            btn_no = QPushButton(no_text)
            btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_no.setStyleSheet(base_style + "QPushButton { background-color: #ecf0f1; color: #7f8c8d; } QPushButton:hover { background-color: #bdc3c7; }")
            btn_no.clicked.connect(self.reject)
            btn_layout.addWidget(btn_no)

            btn_yes = QPushButton(yes_text)
            btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_yes.setStyleSheet(base_style + f"QPushButton {{ background-color: {color}; color: white; }} QPushButton:hover {{ opacity: 0.9; }}")
            btn_yes.clicked.connect(self.accept)
            btn_layout.addWidget(btn_yes)
        else:
            btn_ok = QPushButton("Tamam")
            btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ok.setStyleSheet(base_style + f"QPushButton {{ background-color: {color}; color: white; }} QPushButton:hover {{ opacity: 0.9; }}")
            btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(btn_ok)

        f_layout.addLayout(btn_layout)
        layout.addWidget(frame)

        QTimer.singleShot(0, self._center_on_parent)

    def _center_on_parent(self):
        try:
            if self.parent() and isinstance(self.parent(), QWidget):
                # 🔧 her zaman en üst pencereyi baz al (tablo/scroll içi widget değil)
                parent = self.parent().window()
                global_center = parent.mapToGlobal(parent.rect().center())
                x = global_center.x() - (self.width() // 2)
                y = global_center.y() - (self.height() // 2)
                self.move(x, y)
            else:
                screen = QApplication.primaryScreen().availableGeometry()
                x = screen.center().x() - self.width() // 2
                y = screen.center().y() - self.height() // 2
                self.move(x, y)
        except Exception:
            pass

    @staticmethod
    def show_info(parent, title, msg):
        ModernDialog(parent, title, msg, "INFO").exec()

    @staticmethod
    def show_error(parent, title, msg):
        ModernDialog(parent, title, msg, "ERROR").exec()

    @staticmethod
    def show_success(parent, title, msg):
        ModernDialog(parent, title, msg, "SUCCESS").exec()

    @staticmethod
    def show_warning(parent, title, msg):
        ModernDialog(parent, title, msg, "WARNING").exec()

    @staticmethod
    def show_question(parent, title, msg, yes_btn="Yes", no_btn="No"):
        # ✅ QMessageBox.StandardButton gibi şeyler gelirse stringe çevir
        try:
            from PyQt6.QtWidgets import QMessageBox
            std = getattr(QMessageBox, "StandardButton", None)
            if std is not None:
                if isinstance(yes_btn, std):
                    yes_btn = "Evet" if yes_btn == std.Yes else "Tamam"
                if isinstance(no_btn, std):
                    no_btn = "Hayır" if no_btn == std.No else "İptal"
        except Exception:
            pass

        # ✅ None/boş gelirse de garantiye al
        yes_btn = "Evet" if not str(yes_btn).strip() else str(yes_btn)
        no_btn  = "Hayır" if not str(no_btn).strip() else str(no_btn)

        dialog = ModernDialog(parent, title, msg, "QUESTION", yes_btn, no_btn)
        return dialog.exec() == QDialog.DialogCode.Accepted
