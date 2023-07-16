import sys
import time

from PySide6.QtCore import QObject, QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar
from functools import partial


class Worker1(QObject):
    started = Signal(str)
    progressed = Signal(str)
    finished = Signal(str)
    stopThread = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isPaused = False

    def doWork(self):
        value = 0
        for i in range(0, 25, 1):
            time.sleep(0.250)
            value += 1
            self.progressed.emit(str(value))
            if self.isPaused:
                while self.isPaused:
                    time.sleep(0.1)
        self.finished.emit(str(value))


class Worker2(QObject):
    started = Signal(str)
    progressed = Signal(str)
    finished = Signal(str)
    stopThread = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isPaused = False

    def executeMe(self):
        value = 0
        for i in range(25, 0, -1):
            time.sleep(0.250)
            value += 1
            self.progressed.emit(str(value))
            if self.isPaused:
                while self.isPaused:
                    time.sleep(0.1)
        self.finished.emit(str(value))


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.isPaused = False

        self._stopThread1 = False
        self._stopThread2 = False
        self.layout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.button1 = QPushButton("Contador de 1 a 25", self)
        self.button2 = QPushButton("Contador de 25 a 1", self)
        self.pauseButton = QPushButton("Pausar", self)
        self.closeButton = QPushButton("Fechar", self)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progressBar)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.pauseButton)
        self.layout.addWidget(self.closeButton)

        self.button1.clicked.connect(self.hardWork1)
        self.button2.clicked.connect(self.hardWork2)
        self.pauseButton.clicked.connect(self.pauseWork)
        self.closeButton.clicked.connect(self.close)

        self._worker1 = None
        self._worker2 = None
        self._thread1 = None
        self._thread2 = None

        self.isPaused = False

        self.setFixedSize(300, 200)


    def hardWork1(self):
        self._worker1 = Worker1()
        self._thread1 = QThread()

        self._worker1.stopThread.connect(self.stopThread1)

        self._worker1.moveToThread(self._thread1)

        self._worker1.started.connect(self.worker1Started)
        self._worker1.progressed.connect(self.worker1Progressed)
        self._worker1.finished[str].connect(self.worker1Finished)

        self.isPaused = False
        self.pauseButton.setText("Pausar")
        self.progressBar.setValue(0)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)
        self.pauseButton.setEnabled(True)

        self._thread1.started.connect(self._worker1.doWork)
        self._thread1.finished.connect(self.worker1Finished)
        self._thread1.finished.connect(partial(self.cleanupThread, self._thread1))

        self._thread1.start()

    def worker1Started(self, value):
        self.label.setText(value)
        print('Worker 1 iniciado:', value)

    def worker1Progressed(self, value):
        self.label.setText(value)
        time_left = int(value)
        remaining_text = f"Tempo Restante: {time_left} segundos"
        self.label.setText(remaining_text)
        self.progressBar.setValue(100 - int(value) * 4)

    def stopThread1(self):
        self._stopThread1 = True

    def worker1Finished(self):
        value = 'Start'
        self.label.setText(value)
        self.button1.setEnabled(True)
        self.button2.setEnabled(True)
        self.pauseButton.setEnabled(False)
        print('Worker 1 finalizado:', value)

    def stopThread2(self):
        self._stopThread2 = True

    def hardWork2(self):
        self._worker2 = Worker2()
        self._thread2 = QThread()

        self._worker2.stopThread.connect(self.stopThread2)

        self._worker2.moveToThread(self._thread2)

        self._worker2.started.connect(self.worker2Started)
        self._worker2.progressed.connect(self.worker2Progressed)
        self._worker2.finished[str].connect(self.worker2Finished)

        self.isPaused = False
        self.pauseButton.setText("Pausar")
        self.progressBar.setValue(0)
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)
        self.pauseButton.setEnabled(True)

        self._thread2.started.connect(self._worker2.executeMe)
        self._thread2.finished.connect(self.worker2Finished)
        self._thread2.finished.connect(partial(self.cleanupThread, self._thread2))

        self._thread2.start()

    def worker2Started(self, value):
        self.label.setText(value)
        print('Worker 2 iniciado:', value)

    def worker2Progressed(self, value):
        self.label.setText(value)
        time_left = int(value)
        remaining_text = f"Tempo Restante: {time_left} segundos"
        self.label.setText(remaining_text)
        self.progressBar.setValue(100 - int(value) * 4)

    def worker2Finished(self):
        value = 'Boom'
        self.label.setText(value)
        self.button1.setEnabled(True)
        self.button2.setEnabled(True)
        self.pauseButton.setEnabled(False)
        print('Worker 2 finalizado:', value)

    def pauseWork(self):
        if self.isPaused:
            self.isPaused = False
            self.pauseButton.setText("Pausar")
            if self._worker1 is not None:
                self._worker1.isPaused = False
            elif self._worker2 is not None:
                self._worker2.isPaused = False
        else:
            self.isPaused = True
            self.pauseButton.setText("Continuar")
            if self._worker1 is not None:
                self._worker1.isPaused = True
            elif self._worker2 is not None:
                self._worker2.isPaused = True

    def closeEvent(self, event):
        if self._worker1 is not None:
            self._worker1.stopThread.emit()
            self._thread1.quit()
            self._thread1.wait()

        if self._worker2 is not None:
            self._worker2.stopThread.emit()
            self._thread2.quit()
            self._thread2.wait()

        self.button1.setEnabled(False)
        self.button2.setEnabled(False)
        self.pauseButton.setEnabled(False)
        self.closeButton.setEnabled(False)

        QTimer.singleShot(2000, partial(self.enableButtons, self.button1, self.button2, self.pauseButton, self.closeButton))

    def cleanupThread(self, thread):
        thread.quit()
        thread.wait()

    def enableButtons(self, *buttons):
        for button in buttons:
            button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWidget = MyWidget()
    myWidget.setWindowTitle("Play/Pause RPA")
    # myWidget.setStyleSheet("background-color: purple;")
    # myWidget.progressBar.setStyleSheet("QProgressBar {background-color: #4376E8;}")
    # myWidget.label.setStyleSheet("QLabel {color: black;}")
    myWidget.show()
    sys.exit(app.exec())
