# coding: utf-8
# This file containing a class for gui interface of application SPMC
import sys
from typing import List, Optional
from PyQt5 import QtWidgets, uic
from spmc import Program, CardMarkup
from gui.forms.StartWindow import Ui_Form as StartWindow_form
from gui.forms.EnterSeedPhrase import Ui_Form as EnterSeedPhrase_form
from gui.forms.CardConnection import Ui_Form as CardConnection_form
from gui.forms.EncryptSeedPhrase import Ui_Form as EncryptSeedPhrase_form

class Ui(QtWidgets.QMainWindow):

    class BaseWindow(QtWidgets.QWidget):
        def __init__(self, form):
            super().__init__()
            self.form = form()
            self.form.setupUi(self)
            self.actions = {}

    class StartWindow(BaseWindow):
        def __init__(self):
            super().__init__(StartWindow_form)

        def writeButtonPressed(self):
            self.actions[self.writeButtonPressed.__name__]()

        def readButtonPressed(self):
            self.actions[self.readButtonPressed.__name__]()

        def exitButtonPressed(self):
            self.actions[self.exitButtonPressed.__name__]()

    class EnterSeedPhraseWindow(BaseWindow):
        def __init__(self):
            super().__init__(EnterSeedPhrase_form)
            self.form.seedTextEdit.setPlainText('')

        def cancelButtonPressed(self):
            self.actions[self.cancelButtonPressed.__name__]()

        def nextButtonPressed(self):
            self.actions[self.nextButtonPressed.__name__]()

        def exitButtonPressed(self):
            self.actions[self.exitButtonPressed.__name__]()

        def textEditTextChanged(self):
            try:
                Program.check_seed_phrase(self.form.seedTextEdit.toPlainText())
                self.form.nextButton.setEnabled(True)
                self.form.labelValid.setText('Valid!')
                self.form.labelValid.setStyleSheet("color: green")
            except Program.Error:
                self.form.nextButton.setEnabled(False)
                if self.form.seedTextEdit.toPlainText() != '':
                    self.form.labelValid.setText('Not valid!')
                    self.form.labelValid.setStyleSheet("color: red")
                else:
                    self.form.labelValid.setText('')

    class CardConnectionWindow(BaseWindow):
        def __init__(self):
            super().__init__(CardConnection_form)
            try:
                for card_type in Program.card_types():
                    self.form.cardTypesList.addItem(card_type)
                for card_reader in Program.card_readers():
                    self.form.readersList.addItem(card_reader)
            except Program.Critical as critical:
                QtWidgets.QMessageBox.critical(self,
                                               'Critical error!',
                                               critical.msg,
                                               QtWidgets.QMessageBox.Ok)
                sys.exit(1)
            except Program.Warning as warning:
                QtWidgets.QMessageBox.warning(self,
                                              'Warning!',
                                              warning.msg,
                                              QtWidgets.QMessageBox.Ok)

        def cancelButtonPressed(self):
            self.actions[self.cancelButtonPressed.__name__]()

        def nextButtonPressed(self):
            self.actions[self.nextButtonPressed.__name__]()

        def exitButtonPressed(self):
            self.actions[self.exitButtonPressed.__name__]()

        def updateButtonPressed(self):
            self.form.readersList.clear()
            try:
                for card_reader in Program.card_readers():
                    self.form.readersList.addItem(card_reader)

            except Program.Warning as warning:
                QtWidgets.QMessageBox.warning(self,
                                              'Warning!',
                                              warning.msg,
                                              QtWidgets.QMessageBox.Ok)

        def readersListIndexChanged(self, index):
            if index >= 0:
                Program.disconnect_from_card()
                Program.select_card_reader(self.form.readersList.itemText(index))
                if self.form.cardTypesList.currentIndex() >= 0:
                    Program.connect_to_card()
                    self.form.nextButton.setEnabled(True)

        def cardTypesListIndexChanged(self, index):
            if index >= 0:
                try:
                    Program.disconnect_from_card()
                    Program.select_card_type(self.form.cardTypesList.itemText(index))
                    if self.form.readersList.currentIndex() >= 0:
                        Program.connect_to_card()
                        self.form.nextButton.setEnabled(True)
                except:
                    QtWidgets.QMessageBox.critical(self,
                                                   'Error!',
                                                   'Card work is not possible!',
                                                   QtWidgets.QMessageBox.Ok)
                    sys.exit(1)

    class EncryptSeedPhraseWindow(BaseWindow):
        def __init__(self):
            super().__init__(EncryptSeedPhrase_form)
            try:
                for enc_alg in Program.supported_algorithms():
                    self.form.algorithmsList.addItem(enc_alg)
            except Program.Critical as critical:
                QtWidgets.QMessageBox.critical(self,
                                               'Critical error!',
                                               critical.msg,
                                               QtWidgets.QMessageBox.Ok)
                sys.exit(1)

        def cancelButtonPressed(self):
            self.actions[self.cancelButtonPressed.__name__]()

        def encryptButtonPressed(self):
            self.actions[self.encryptButtonPressed.__name__]()

        def exitButtonPressed(self):
            self.actions[self.exitButtonPressed.__name__]()

        def textEditTextChanged(self):
            if len(self.form.contactDataTextEdit.toPlainText().encode('utf8')) > 20:
                self.form.encryptButton.setEnabled(False)
                self.form.labelCorrect.setText('Very large contact information!')
                self.form.labelCorrect.setStyleSheet("color: red")
            else:
                self.form.labelCorrect.setText('')
                self.form.encryptButton.setEnabled(True)

    class ProgramMode:
        Read = 1
        Write = 2

    def __init__(self):
        super(Ui, self).__init__()
        self.seed_phrase: Optional[str] = None
        self.program_mode: Optional[Ui.ProgramMode] = None
        self.pred_windows: List[Ui.BaseWindow] = []
        self.current_window: Optional[Ui.BaseWindow] = None

        self.start_window: Optional[Ui.BaseWindow] = None
        self.enter_seed_phrase_window: Optional[Ui.BaseWindow] = None
        self.card_connection_window: Optional[Ui.BaseWindow] = None
        self.encrypt_seed_phrase_window: Optional[Ui.BaseWindow] = None

        self.set_start_program_state()

    def set_start_program_state(self):
        self.seed_phrase = None
        self.program_mode = None
        self.pred_windows = []
        self.current_window = None

        self.start_window = Ui.StartWindow()
        self.enter_seed_phrase_window = Ui.EnterSeedPhraseWindow()
        self.card_connection_window = Ui.CardConnectionWindow()
        self.encrypt_seed_phrase_window = Ui.EncryptSeedPhraseWindow()

        self.start_window.actions["writeButtonPressed"] = lambda: self.change_window(
            self.enter_seed_phrase_window)
        self.start_window.actions["readButtonPressed"] = self.go_card_connection
        self.start_window.actions["exitButtonPressed"] = self.close

        self.enter_seed_phrase_window.actions["cancelButtonPressed"] = self.go_pred_window
        self.enter_seed_phrase_window.actions["nextButtonPressed"] = self.go_card_connection
        self.enter_seed_phrase_window.actions["exitButtonPressed"] = self.close

        self.card_connection_window.actions["cancelButtonPressed"] = self.go_pred_window
        self.card_connection_window.actions["nextButtonPressed"] = self.go_next_action_card_connection
        self.card_connection_window.actions["exitButtonPressed"] = self.close

        self.encrypt_seed_phrase_window.actions["cancelButtonPressed"] = self.go_pred_window
        self.encrypt_seed_phrase_window.actions["encryptButtonPressed"] = self.encrypt_seed_phrase
        self.encrypt_seed_phrase_window.actions["exitButtonPressed"] = self.close

        self.change_window(self.start_window)
        self.show()

    def change_window(self, window_: BaseWindow, is_pred_window: bool = False):
        if window_ == self.start_window:
            self.program_mode = None
        if self.current_window == self.start_window:
            if window_ == self.enter_seed_phrase_window:
                self.program_mode = Ui.ProgramMode.Write
            elif window_ == self.card_connection_window:
                self.program_mode = Ui.ProgramMode.Read

        if self.current_window:
            self.current_window.setParent(None)
            if not is_pred_window:
                self.pred_windows.append(self.current_window)

        self.setCentralWidget(window_)
        self.setFixedSize(window_.size())
        self.setWindowTitle(window_.windowTitle())
        self.current_window = window_

    def go_pred_window(self):
        if self.current_window == self.card_connection_window:
            self.seed_phrase = None
        self.change_window(self.pred_windows.pop(), True)

    def closeEvent(self, event):
        try:
            self.seed_phrase = None
            Program.exit(0)
        except Program.Dialog as dialog:
            response = QtWidgets.QMessageBox.question(self,
                                                      'Exit from the program',
                                                      dialog.msg,
                                                      QtWidgets.QMessageBox.Yes,
                                                      QtWidgets.QMessageBox.No)
            event.ignore()
            if response == QtWidgets.QMessageBox.Yes:
                exec(dialog.choices[list(dialog.choices.keys())[0]])
            else:
                exec(dialog.choices[list(dialog.choices.keys())[1]])

    def go_card_connection(self):
        if self.current_window == self.enter_seed_phrase_window:
            self.seed_phrase = self.enter_seed_phrase_window.form.seedTextEdit.toPlainText()
            self.enter_seed_phrase_window.form.seedTextEdit.clear()
        self.change_window(self.card_connection_window)

    def encrypt_seed_phrase(self):
        password = self.encrypt_seed_phrase_window.form.passwordEdit.text()
        self.encrypt_seed_phrase_window.form.passwordEdit.setText('')
        seed_phrase = self.seed_phrase
        self.seed_phrase = None
        write_func = lambda: Program.write_seed_phrase(seed_phrase,
                                                         self.encrypt_seed_phrase_window.form.algorithmsList.currentText(),
                                                         password,
                                                         self.encrypt_seed_phrase_window.form.contactDataTextEdit.toPlainText())

        success_info = lambda: QtWidgets.QMessageBox.information(self,
                                                                 'Successful!',
                                                                 'Seed-phrase successfully written to the card',
                                                                 QtWidgets.QMessageBox.Close)
        try:
            write_func()
            success_info()
        except Program.Input as input_:
            text, ok = QtWidgets.QInputDialog().getText(self,
                                                        input_.name,
                                                        str(input_),
                                                        QtWidgets.QLineEdit.Normal)
            if ok and text:
                try:
                    input_.get_value(text)
                    write_func()
                    success_info()
                except:
                    QtWidgets.QMessageBox.critical(self,
                                                  'Critical Error!',
                                                  'Not successful! (Wrong card PIN)',
                                                  QtWidgets.QMessageBox.Ok)
        self.set_start_program_state()

    def go_next_action_card_connection(self):
        if self.program_mode == Ui.ProgramMode.Write:
            self.change_window(self.encrypt_seed_phrase_window)
        elif self.program_mode == Ui.ProgramMode.Read:
            read_metadata_func = lambda: Program.read_seed_phrase()
            verify_encrypt_password_func = lambda: QtWidgets.QInputDialog().getText(self,
                                                                                    'Verify encrypt password',
                                                                                    str('Enter card password:'),
                                                                                    QtWidgets.QLineEdit.Password)
            your_seed_phrase_func = lambda: QtWidgets.QMessageBox.information(self,
                                                                              'Your seed phrase',
                                                                              Program.read_seed_phrase(password),
                                                                              QtWidgets.QMessageBox.Close)
            contact_data_func = lambda text: QtWidgets.QMessageBox.information(self,
                                                                               'Contact data',
                                                                               text,
                                                                               QtWidgets.QMessageBox.Close)

            try:
                metadata = read_metadata_func()
                if metadata.contact_data:
                    contact_data_func(metadata.contact_data)

                password, ok = verify_encrypt_password_func()
                if ok:
                    your_seed_phrase_func()

            except Program.Input as input_:
                text, ok = QtWidgets.QInputDialog().getText(self,
                                                            input_.name,
                                                            str(input_),
                                                            QtWidgets.QLineEdit.Normal)
                if ok:
                    try:
                        input_.get_value(text)
                        metadata = read_metadata_func()
                        if metadata.contact_data:
                            contact_data_func(metadata.contact_data)
                        password, ok = verify_encrypt_password_func()
                        if ok and password:
                            Program.read_seed_phrase(password)
                            your_seed_phrase_func()
                    except (CardMarkup.CardIsNotMarkup, CardMarkup.DataIsCorrupted) as err:
                        QtWidgets.QMessageBox.warning(self,
                                                      'Warning!',
                                                      err.msg,
                                                      QtWidgets.QMessageBox.Ok)
                    except:
                        QtWidgets.QMessageBox.warning(self,
                                                      'Warning!',
                                                      'Wrong card PIN!',
                                                      QtWidgets.QMessageBox.Ok)
            except (CardMarkup.CardIsNotMarkup, CardMarkup.DataIsCorrupted) as err:
                QtWidgets.QMessageBox.warning(self,
                                              'Warning!',
                                              err.msg,
                                              QtWidgets.QMessageBox.Ok)


class myApp(QtWidgets.QApplication):
    def __init__(self, args_list):
        super(myApp, self).__init__(args_list)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()
