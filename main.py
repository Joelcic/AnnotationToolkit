import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget)
from views.video_view import VideoPlayerView
from views.annotation_view import AnnotationToolView
from views.welcome_view import WelcomePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annotation Toolkit")
        self.setGeometry(100, 100, 800, 600)

        self.stack = QStackedWidget()

        self.video_view = VideoPlayerView()
        self.video_view.back_to_menu.connect(lambda: self.stack.setCurrentWidget(self.menu_view))

        self.annotation_view = AnnotationToolView()
        self.annotation_view.back_to_menu.connect(lambda: self.stack.setCurrentWidget(self.menu_view))

        # Real welcome page with buttons
        self.menu_view = WelcomePage(
            switch_to_video_callback=lambda: self.stack.setCurrentWidget(self.video_view),
            switch_to_annotation_callback=lambda: self.stack.setCurrentWidget(self.annotation_view)
        )

        # Add views to stack
        self.stack.addWidget(self.menu_view)
        self.stack.addWidget(self.video_view)
        self.stack.addWidget(self.annotation_view)

        self.stack.setCurrentWidget(self.menu_view)
        self.setCentralWidget(self.stack)

def main():
    app = QApplication(sys.argv)

    # Load stylesheet
    with open("common/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()