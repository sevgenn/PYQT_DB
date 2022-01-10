"""Модуль окна, в котором обрабатывается удаление клиента."""

import logging
from PyQt5.QtWidgets import QDialog, qApp, QMessageBox
from client.remove_form import Ui_Dialog


class RemoveContactDialog(QDialog):
    """Класс, описывающий форму удаления контакта из списка."""

    def __init__(self, database):
        super().__init__()
        self.logger = logging.getLogger('client')
        self.database = database

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.selector = self.ui.comboBox
        self.selector.addItems(sorted(self.database.get_contacts()))

        self.ui.btn_cancel.clicked.connect(self.close)
