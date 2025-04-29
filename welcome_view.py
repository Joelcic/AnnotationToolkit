from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from style import *

class WelcomePage(QWidget):
    def __init__(self, switch_to_video_callback, switch_to_annotation_callback):
        super().__init__()

        # Title
        title = QLabel("Welcome to Joels Annotation Toolkit")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("WelcomeTitle")

        # Subtitle
        subtitle = QLabel("Choose a mode to get started:")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("WelcomeSubTitle")

        # Buttons
        video_btn = QPushButton("🎥  Video to Frame")
        annot_btn = QPushButton("🖼️  Image Annotation Tool")

        for btn in (video_btn, annot_btn):
            btn.setFixedHeight(50)
            btn.setObjectName("ToolButton")

        video_btn.clicked.connect(switch_to_video_callback)
        annot_btn.clicked.connect(switch_to_annotation_callback)

        # Layout
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.addWidget(video_btn)
        btn_layout.addWidget(annot_btn)
        btn_layout.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        self.setLayout(layout)
