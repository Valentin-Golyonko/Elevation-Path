import sys
from PyQt5.QtWidgets import QApplication
from create_ui import CreateUi

app = QApplication(sys.argv)

elev = CreateUi()

app.exit(app.exec_())
