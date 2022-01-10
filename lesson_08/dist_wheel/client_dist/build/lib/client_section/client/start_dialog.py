from PyQt5.QtWidgets import QApplication, QDialog, qApp
from client.start_form import Ui_Dialog


class StartDialog(QDialog):
    """Класс, описывающий диалог при запуске клиента."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ok_pressed = False
        self.ui.btn_ok.clicked.connect(self.on_click)
        self.ui.btn_cancel.clicked.connect(qApp.exit)
        self.account_name = self.ui.lineEdit_name
        self.account_pass = self.ui.lineEdit_pass

        self.show()

    def on_click(self):
        """Обрабатывает нажатие кнопки Start."""
        if self.account_name.text() and self.account_pass.text():
            self.ok_pressed = True
            qApp.quit()

# if __name__ == '__main__':
#     app = QApplication([])
#     window = StartDialog()
#     app.exec_()
