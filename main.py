from embebidos import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
import receiver as re
import random
import threading

class Controller:

    def __init__(self, parent, app):
        self.ui = Ui_Dialog()
        self.parent = parent
        self.app = app

        self.xlist, self.accx, self.accy, self.accz = [], [], [], []
        self.RMSx, self.RMSy, self.RMSz = [], [], []
        self.FFTx, self.FFTy, self.FFTz = [], [], []
        self.xlistpeaks, self.Peaksx, self.Peaksy, self.Peaksz = [], [], [], []
        self.xlistfft = []

        self.index = 0
        self.peakindex = 0
        self.WINDOW = re.WINDOW
        self.PEAKWINDOW = 5

        self.time = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
        self.running = True

        

    def setSignals(self):
        self.ui.selec_12.currentIndexChanged.connect(self.leerModoOperacion)
        self.ui.pushButton.clicked.connect(self.leerConfiguracion)
        self.ui.pushButton_2.clicked.connect(self.onRead)
        self.parent.finished.connect(self.closeEvent)

    def leerConfiguracion(self):
        conf = dict()
        conf['AccSamp'] = self.ui.comboBox_acc_sampling.currentIndex()+1
        conf['AccSen'] = self.ui.text_acc_sensibity.currentIndex()+1
        conf['Modo'] = self.ui.selec_13.currentIndex()+1
        print (conf)
        re.init_connection(conf['AccSen'], conf['AccSamp'], conf['Modo'])
        
        
        return conf

    def leerModoOperacion(self):
        index = self.ui.selec_12.currentIndex()
        texto = self.ui.selec_12.itemText(index)
        print(texto)
        if texto == "BMI270":
            self.ui.onBMI270Select()
        else:
            self.ui.onBMI688Select()

        return texto
    
        

    def criticalError(self):
        popup = QtWidgets.QMessageBox(parent= self.parent)
        popup.setWindowTitle('Error Critico')
        popup.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        popup.exec()
        return

    def onRead(self):
        self.thread = threading.Thread(target=self.stop)
        self.thread.start()

    def closeEvent(self, event):
        print('Cerrando el programa')
        self.running = False
        self.thread.join()

    def stop(self):
        print('Captando datos')
        while self.running:
            data = re.init_receiver()
            if data is None:
                self.app.processEvents()
                continue
            new_accx, new_accy, new_accz, newRMSx, newRMSy, newRMSz, newFFTx, newFFTy, newFFTz, newPeaksx, newPeaksy, newPeaksz = data

  
            self.accx += new_accx
            self.accy += new_accy
            self.accz += new_accz

            self.RMSx += newRMSx
            self.RMSy += newRMSy
            self.RMSz += newRMSz

            self.index += len(new_accx)

            self.accx = self.accx[-(3*self.WINDOW):]
            self.accy = self.accy[-(3*self.WINDOW):]
            self.accz = self.accz[-(3*self.WINDOW):]

            self.RMSx = self.RMSx[-(3*self.WINDOW):]
            self.RMSy = self.RMSy[-(3*self.WINDOW):]
            self.RMSz = self.RMSz[-(3*self.WINDOW):]

            self.xlist = [i for i in range((max(0, self.index - 3*self.WINDOW)), self.index)]

            self.Peaksx += newPeaksx
            self.Peaksy += newPeaksy
            self.Peaksz += newPeaksz

            self.peakindex += len(newPeaksx)

            self.Peaksx = self.Peaksx[-(3*self.PEAKWINDOW):]
            self.Peaksy = self.Peaksy[-(3*self.PEAKWINDOW):]
            self.Peaksz = self.Peaksz[-(3*self.PEAKWINDOW):]
            self.xlistpeaks = [i for i in range((max(0, self.peakindex - 3*self.PEAKWINDOW)), self.peakindex)]
            

            self.xlistfft = list(range(0, int(self.WINDOW/2)))
            self.FFTx = newFFTx[0:int(self.WINDOW/2)]
            self.FFTy = newFFTy[0:int(self.WINDOW/2)]
            self.FFTz = newFFTz[0:int(self.WINDOW/2)]
            
            self.ui.curve11.setData(self.xlist, self.accx)
            self.ui.curve12.setData(self.xlist, self.accy)
            self.ui.curve13.setData(self.xlist, self.accz)

            self.ui.curve21.setData(self.xlist, self.RMSx)
            self.ui.curve22.setData(self.xlist, self.RMSy)
            self.ui.curve23.setData(self.xlist, self.RMSz)

            self.ui.curve31.setData(self.xlistfft, self.FFTx)
            self.ui.curve32.setData(self.xlistfft, self.FFTy)
            self.ui.curve33.setData(self.xlistfft, self.FFTz)

            self.ui.curve41.setData(self.xlistpeaks, self.Peaksx)
            self.ui.curve42.setData(self.xlistpeaks, self.Peaksy)
            self.ui.curve43.setData(self.xlistpeaks, self.Peaksz)
            

            self.app.processEvents()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    cont = Controller(parent=Dialog, app=app)
    ui = cont.ui
    ui.setupUi(Dialog)
    Dialog.show()
    cont.setSignals()
    sys.exit(app.exec_())