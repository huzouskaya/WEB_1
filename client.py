# client.py
import util
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
import sys


class clientWindow(QMainWindow):
    def __init__(self):
        super(clientWindow, self).__init__()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        self.ip_le = QLineEdit(self)
        self.ip_le.setPlaceholderText(util.ip)

        self.connect_button = QPushButton("Подключиться", self)
        self.send_button = QPushButton("отправить данные", self)

        self.layout.addWidget(self.ip_le)
        self.layout.addWidget(self.connect_button)
        self.layout.addWidget(self.send_button)

        self.connect_button.clicked.connect(self.connectToServer)
        self.send_button.clicked.connect(self.messageToServer)

    def connectToServer(self):
        self.server = QTcpSocket(self)
        ip = util.ip
        self.server.connectToHost(ip, util.PORT)

    def messageToServer(self):
        msg = self.send_button.text()

        if not self.server.isValid():
            print("Не удалось подключиться к серверу.")
            return

        self.request = QByteArray()
        stream = QDataStream(self.request, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_12)

        stream.writeUInt32(0)
        stream.writeQString(msg)

        stream.device().seek(0)
        stream.writeUInt32(self.request.size() - 4)

        self.server.write(self.request)

        self.nextBlockSize = 0
        self.request = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = clientWindow()
    w.show()
    sys.exit(app.exec_())
