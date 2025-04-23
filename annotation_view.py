import os
import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget,
    QFileDialog, QComboBox, QLineEdit, QMessageBox, QDialog, QDialogButtonBox, QGraphicsView
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal

class ClassSelectDialog(QDialog):
    def __init__(self, class_list):
        super().__init__()
        self.setWindowTitle("Select Class")
        self.combo = QComboBox()
        self.combo.addItems(class_list)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select class:"))
        layout.addWidget(self.combo)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def selected_class_index(self):
        return self.combo.currentIndex()


class AnnotationToolView(QWidget):
    back_to_menu = pyqtSignal()  # Signal to go back

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annotation Tool")
        self.resize(1200, 800)

        self.setStyleSheet("""
            QLabel { font-size: 14px; }
            QComboBox, QLineEdit, QListWidget { font-size: 14px; }
        """)

        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px 14px;
                border-radius: 8px;
                border: 2px solid #ccc;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e6f0ff;
                border: 2px solid #3399ff;
            }
            QPushButton:pressed {
                background-color: #cce0ff;
                border: 2px solid #3399ff;
            }
        """

        # Back button
        self.back_btn = QPushButton("⬅ Back")
        self.back_btn.setStyleSheet(button_style)
        self.back_btn.clicked.connect(self.emit_back_signal)
        topbar_wrapper = QHBoxLayout()
        topbar_wrapper.addWidget(self.back_btn)
        topbar_wrapper.setAlignment(Qt.AlignLeft)

        # Format dropdown
        format_layout = QHBoxLayout()
        format_label = QLabel("Format: ")
        self.format_selector = QComboBox()
        self.format_selector.addItems(["YOLO"])
        format_layout.addWidget(format_label, stretch=1)
        format_layout.addWidget(self.format_selector, stretch=2)
        format_layout.addStretch(stretch=3)

        # Class management
        self.class_count_label = QLabel("Classes: 0")
        self.add_class_input = QLineEdit()
        self.add_class_input.setPlaceholderText("Add new class here...")
        self.add_class_button = QPushButton("Add")
        self.add_class_button.setStyleSheet(button_style)
        self.class_list = QListWidget()
        self.class_list.setStyleSheet("color: gray; font-style: italic; background: white;")
        self.class_list.addItem("No classes added yet...")
        self.class_list.setEnabled(False)

        self.image_source_btn = QPushButton("🖼️ Add image source")
        self.image_source_btn.setStyleSheet(button_style)
        self.image_source_label = QLabel("No source selected")
        self.output_folder_btn = QPushButton("📁 Add output source")
        self.output_folder_btn.setStyleSheet(button_style)
        self.output_folder_label = QLabel("No folder selected")

        self.image_source_btn.clicked.connect(self.select_image_folder)
        self.output_folder_btn.clicked.connect(self.select_output_folder)
        self.add_class_button.clicked.connect(self.add_class)

        add_wrapper = QHBoxLayout()
        add_wrapper.addWidget(self.add_class_input, stretch=4)
        add_wrapper.addStretch(stretch=1)
        add_wrapper.addWidget(self.add_class_button, stretch=2)

        img_src_wrapper = QHBoxLayout()
        img_src_wrapper.addWidget(self.image_source_btn, stretch=2)
        img_src_wrapper.addStretch(stretch=4)

        out_src_wrapper = QHBoxLayout()
        out_src_wrapper.addWidget(self.output_folder_btn, stretch=2)
        out_src_wrapper.addStretch(stretch=4)

        left_panel = QVBoxLayout()
        left_panel.addSpacing(25)
        left_panel.addLayout(format_layout)
        left_panel.addWidget(self.class_count_label)
        left_panel.addLayout(add_wrapper)
        left_panel.addWidget(self.class_list)
        left_panel.addLayout(img_src_wrapper)
        left_panel.addWidget(self.image_source_label)
        left_panel.addLayout(out_src_wrapper)
        left_panel.addWidget(self.output_folder_label)
        left_panel.addStretch()

        # Image display
        self.image_label = QLabel("Image")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray; background: white;")
        self.image_label.mousePressEvent = self.start_drawing
        self.image_label.mouseMoveEvent = self.drawing
        self.image_label.mouseReleaseEvent = self.end_drawing

        image_area = QVBoxLayout()
        image_area.addWidget(self.image_label)

        # Bottom controls
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setStyleSheet(button_style)
        self.next_btn = QPushButton("▶")
        self.next_btn.setStyleSheet(button_style)
        self.image_index_label = QLabel("Image: x")
        self.annotation_count_label = QLabel("Nr annotations in image: 0")
        self.save_button = QPushButton("💾 Save")
        self.save_button.setStyleSheet(button_style)

        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        self.save_button.clicked.connect(self.save_annotations)

        bottom_controls = QHBoxLayout()
        bottom_controls.addWidget(self.prev_btn)
        bottom_controls.addWidget(self.image_index_label)
        bottom_controls.addWidget(self.next_btn)
        bottom_controls.addWidget(self.annotation_count_label)
        bottom_controls.addStretch()
        bottom_controls.addWidget(self.save_button)

        core_layout = QHBoxLayout()
        core_layout.addLayout(left_panel, stretch=3)

        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(10, 10, 10, 10)
        center_layout.addLayout(image_area, stretch=8)
        center_layout.addLayout(bottom_controls, stretch=1)

        core_layout.addLayout(center_layout, stretch=7)

        main_layout = QVBoxLayout()
        main_layout.addLayout(topbar_wrapper)
        main_layout.addLayout(core_layout)

        self.setLayout(main_layout)

        # State
        self.classes = []
        self.annotations = []
        self.image_folder = None
        self.output_folder = None
        self.image_paths = []
        self.current_index = 0
        self.drawing_start = None
        self.current_pixmap = None
        self.annotation_rects = []

    def emit_back_signal(self):
        self.back_to_menu.emit()

    def add_class(self):
        name = self.add_class_input.text().strip()
        if name:
            if not self.classes:  # first time, remove placeholder
                self.class_list.clear()
                self.class_list.setStyleSheet("")  # reset style
                self.class_list.setEnabled(True)
            index = len(self.classes)
            self.classes.append(name)
            self.class_list.addItem(f"{index}: {name}")
            self.class_count_label.setText(f"Classes: {len(self.classes)}")
            self.add_class_input.clear()

    def select_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.image_folder = folder
            self.image_paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg'))]
            self.image_paths.sort()
            self.current_index = 0

            self.image_source_label.setText(f"{folder}")

            self.load_image()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(f"{folder}")

    def load_image(self):
        if not self.image_paths:
            return
        path = self.image_paths[self.current_index]
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qimg = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.current_pixmap = QPixmap.fromImage(qimg)

        # Always scale to fit the fixed image_label size
        scaled_pixmap = self.current_pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.annotation_rects = []
        self.annotations = []
        self.image_index_label.setText(f"Image: {self.current_index + 1}/{len(self.image_paths)}")
        self.annotation_count_label.setText(f"Nr annotations: {len(self.annotations)}")
        self.redraw_image_with_boxes()


    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_image()

    def start_drawing(self, event):
        if self.current_pixmap:
            pos = self.image_label.mapFromGlobal(event.globalPos())
            x_offset, y_offset, x_scale, y_scale = self.get_image_draw_info()

            x = pos.x() - x_offset
            y = pos.y() - y_offset

            if x < 0 or y < 0 or x > (self.image_label.width() - x_offset * 2) or y > (
                    self.image_label.height() - y_offset * 2):
                return  # Clicked outside image area

            self.drawing_start = QPoint(int(x * x_scale), int(y * y_scale))

    def drawing(self, event):
        if self.drawing_start and self.current_pixmap:
            pos = self.image_label.mapFromGlobal(event.globalPos())
            x_offset, y_offset, x_scale, y_scale = self.get_image_draw_info()
            x = pos.x() - x_offset
            y = pos.y() - y_offset
            temp_point = QPoint(int(x * x_scale), int(y * y_scale))

            temp_pixmap = self.current_pixmap.copy()
            painter = QPainter(temp_pixmap)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

            for rect, _ in self.annotation_rects:
                painter.drawRect(rect)

            painter.drawRect(QRect(self.drawing_start, temp_point).normalized())
            painter.end()

            scaled_pixmap = temp_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def end_drawing(self, event):
        if self.drawing_start and self.current_pixmap:
            pos = self.image_label.mapFromGlobal(event.globalPos())
            x_offset, y_offset, x_scale, y_scale = self.get_image_draw_info()
            x = pos.x() - x_offset
            y = pos.y() - y_offset
            if x < 0 or y < 0:
                return
            end_point = QPoint(int(x * x_scale), int(y * y_scale))

            dialog = ClassSelectDialog(self.classes)
            if dialog.exec_() == QDialog.Accepted:
                class_id = dialog.selected_class_index()
                rect = QRect(self.drawing_start, end_point).normalized()

                self.annotation_rects.append((rect, class_id))

                # Convert to YOLO format using original image size
                img_w = self.current_pixmap.width()
                img_h = self.current_pixmap.height()

                x_center = (rect.left() + rect.width() / 2) / img_w
                y_center = (rect.top() + rect.height() / 2) / img_h
                w = rect.width() / img_w
                h = rect.height() / img_h

                self.annotations.append((class_id, x_center, y_center, w, h))
                self.annotation_count_label.setText(f"Nr annotations: {len(self.annotations)}")

                self.redraw_image_with_boxes()
        self.drawing_start = None

    def save_annotations(self):
        if not self.output_folder or not self.image_paths:
            QMessageBox.warning(self, "Missing paths", "Please select image source and output folder.")
            return

        image_filename = f"{self.current_index + 1}.jpg"
        label_filename = f"{self.current_index + 1}.txt"

        os.makedirs(os.path.join(self.output_folder, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, "labels"), exist_ok=True)

        image_path = os.path.join(self.output_folder,"images", image_filename)
        label_path = os.path.join(self.output_folder, "labels", label_filename)

        # Save image
        orig_img = cv2.imread(self.image_paths[self.current_index])
        cv2.imwrite(image_path, orig_img)

        # Save annotations
        with open(label_path, 'w') as f:
            for ann in self.annotations:
                f.write(f"{ann[0]} {ann[1]:.6f} {ann[2]:.6f} {ann[3]:.6f} {ann[4]:.6f}\n")

        #QMessageBox.information(self, "Saved", f"Saved to {label_path}")
        self.next_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Resize image label to be 75% of window size
        new_w = int(self.width() * 0.75)
        new_h = int(self.height() * 0.75)
        self.image_label.setFixedSize(new_w, new_h)

        # Redraw image
        if self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def redraw_image_with_boxes(self):
        if not self.current_pixmap:
            return

        temp_pixmap = self.current_pixmap.copy()
        painter = QPainter(temp_pixmap)

        for rect, class_id in self.annotation_rects:
            color = self.get_class_color(class_id)
            pen = QPen(color, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

        painter.end()

        scaled_pixmap = temp_pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def get_image_draw_info(self):
        label_size = self.image_label.size()
        pixmap_size = self.current_pixmap.size()

        # Compute the scale that was used
        scaled_pixmap = self.current_pixmap.scaled(
            label_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        scaled_size = scaled_pixmap.size()

        x_offset = (label_size.width() - scaled_size.width()) // 2
        y_offset = (label_size.height() - scaled_size.height()) // 2

        x_scale = self.current_pixmap.width() / scaled_size.width()
        y_scale = self.current_pixmap.height() / scaled_size.height()

        return x_offset, y_offset, x_scale, y_scale


    def get_class_color(self, class_id):
        # Generates a distinct QColor using HSV hue rotation
        hue = (class_id * 137) % 360  # 137 is a good spacing constant
        color = QColor()
        color.setHsl(hue, 255, 180)  # Full saturation, medium lightness
        return color