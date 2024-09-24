# server.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QLabel, QGraphicsPixmapItem
from PyQt5.QtNetwork import QTcpServer, QHostAddress
from PyQt5.QtCore import QDataStream, QByteArray, QIODevice, pyqtSlot
from functools import partial
import random
from PyQt5.QtGui import QPixmap
import util

img = ['img1.png', 'img2.png', 'img3.png', 'img4.jpg']


class ServerWindow(QMainWindow):
    def __init__(self):
        super(ServerWindow, self).__init__()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        self.ip_le = QLineEdit(self)
        self.out_td = QTextEdit(self)
        self.out_td.setReadOnly(True)
        self.ip_le.setPlaceholderText(util.ip)

        self.layout.addWidget(self.ip_le)
        self.layout.addWidget(self.out_td)

        self.ip_le.setText(util.ip)

        self.tcpserver = QTcpServer(self)
        self.tcpserver.listen(QHostAddress.Any, util.PORT)
        self.tcpserver.newConnection.connect(self.createConnection)

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

    def createConnection(self):
        connection = self.tcpserver.nextPendingConnection()
        connection.nextBlockSize = 0
        connection.readyRead.connect(partial(self.receiveMessage, connection))

        adr = connection.peerAddress().toString()
        self.consoleMessage(f'Connected to: {adr}')

    def consoleMessage(self, text):
        self.out_td.append(text)

    def receiveMessage(self, socket):
        stream = QDataStream(socket)
        stream.setVersion(QDataStream.Qt_5_15)

        if socket.bytesAvailable() < 4:
            return

        nextBlockSize = stream.readUInt32()
        if socket.bytesAvailable() < nextBlockSize:
            return

        textFromClient = stream.readQString()
        self.setProgress((textFromClient))

    def setProgress(self, value):
        if value == "отправить данные":
            random_element = random.choice(img)
            pixmap = QPixmap(random_element)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = ServerWindow()
    w.show()
    sys.exit(app.exec_())
