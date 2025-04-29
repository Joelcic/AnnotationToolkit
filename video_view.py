import os
import cv2
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap


class VideoPlayerView(QWidget):
    back_to_menu = pyqtSignal()  # Signal to go back

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video → Frame")
        self.setGeometry(100, 100, 1000, 700)

        # --- VIDEO DISPLAY ---
        self.video_label = QLabel("Video")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("VideoLabel")

        video_area = QVBoxLayout()
        video_area.addWidget(self.video_label)

        # --- CONTROLS ---
        self.prev_btn = QPushButton("◀")
        self.frame_label = QLabel("Frame: 0")
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.next_btn = QPushButton("▶")
        self.speed_label = QLabel("Speed: 1x")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.play_btn = QPushButton("⏯ Play / Pause")
        self.save_btn = QPushButton("💾 Save Frame")

        self.prev_btn.clicked.connect(self.prev_frame)
        self.next_btn.clicked.connect(self.next_frame_manual)
        self.play_btn.clicked.connect(self.toggle_play)
        self.save_btn.clicked.connect(self.save_frame)

        bottom_controls = QHBoxLayout()
        bottom_controls.addWidget(self.prev_btn)
        bottom_controls.addWidget(self.frame_label)
        bottom_controls.addWidget(self.next_btn)
        bottom_controls.addWidget(self.speed_label)
        bottom_controls.addStretch()
        bottom_controls.addWidget(self.play_btn)
        bottom_controls.addStretch()
        bottom_controls.addWidget(self.save_btn)

        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(bottom_controls)

        # --- SIDEBAR ---
        self.back_btn = QPushButton("⬅ Back")
        self.back_btn.clicked.connect(self.emit_back_signal)

        self.load_btn = QPushButton("🎥 Load Video")
        self.load_btn.clicked.connect(self.load_video)
        self.load_label = QLabel("No video selected")

        self.output_folder_btn = QPushButton("📁 Add output source")
        self.output_folder_btn.clicked.connect(self.select_output_folder)
        self.output_folder_label = QLabel("No folder selected")

        load_src_wrapper = QHBoxLayout()
        load_src_wrapper.addWidget(self.load_btn)
        load_src_wrapper.addStretch()

        out_src_wrapper = QHBoxLayout()
        out_src_wrapper.addWidget(self.output_folder_btn)
        out_src_wrapper.addStretch()

        left_panel = QVBoxLayout()
        left_panel.addSpacing(50)
        left_panel.addLayout(load_src_wrapper)
        left_panel.addWidget(self.load_label)
        left_panel.addSpacing(10)
        left_panel.addLayout(out_src_wrapper)
        left_panel.addWidget(self.output_folder_label)
        left_panel.addStretch()

        left_wrapper = QVBoxLayout()
        left_wrapper.addLayout(left_panel)

        topbar_wrapper = QHBoxLayout()
        topbar_wrapper.addWidget(self.back_btn)
        topbar_wrapper.setAlignment(Qt.AlignLeft)

        # --- MAIN CONTENT ---
        center_layout = QVBoxLayout()
        center_layout.addLayout(video_area, stretch=8)
        center_layout.addWidget(self.bottom_widget, stretch=1)

        center_wrapper = QVBoxLayout()
        center_wrapper.setContentsMargins(10, 10, 10, 10)
        center_wrapper.addLayout(center_layout)

        core_layout = QHBoxLayout()
        core_layout.addLayout(left_wrapper, stretch=3)
        core_layout.addLayout(center_wrapper, stretch=7)
        core_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(topbar_wrapper)
        main_layout.addLayout(core_layout)

        self.setLayout(main_layout)

        # --- STATE ---
        self.cap = None
        self.current_frame = None
        self.frame_pos = 0
        self.frame_count = 0
        self.output_folder = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame_auto)

    def emit_back_signal(self):
        self.back_to_menu.emit()

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if path:
            self.cap = cv2.VideoCapture(path)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.load_label.setText(path)
            self.timer.start(33)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(folder)

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(33)

    def next_frame_auto(self):
        self.read_and_display()

    def next_frame_manual(self):
        self.timer.stop()
        self.read_and_display()

    def prev_frame(self):
        if self.cap:
            pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(pos - 2, 0))
            self.read_and_display()

    def read_and_display(self):
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                self.timer.stop()
                return
            self.current_frame = frame
            self.frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.frame_label.setText(f"Frame: {self.frame_pos}")
            self.show_frame(frame)

    def show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def save_frame(self):
        if not self.output_folder:
            QMessageBox.warning(self, "Missing paths", "Please select output folder.")
            return

        if self.current_frame is not None:
            name = f"frame_{self.frame_pos}.jpg"
            cv2.imwrite(os.path.join(self.output_folder, name), self.current_frame)
            print(f"Saved {name}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        window_w = self.width()
        window_h = self.height()
        video_w = int(window_w * 0.75)
        video_h = int(window_h * 0.75)
        self.video_label.setFixedSize(video_w, video_h)
        self.bottom_widget.setFixedWidth(video_w)
        if self.current_frame is not None:
            self.show_frame(self.current_frame)