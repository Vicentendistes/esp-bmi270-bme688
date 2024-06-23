from embebidos import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
import receiver as re
import queue

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

        self.temp = []
        self.humd = []
        self.gas_res = []
        self.pres = []
        self.PeaksTemp = []
        self.PeaksHumd = []
        self.PeaksGas_Res = []
        self.PeaksPres = []
        
        self.q = queue.Queue()
        self.conf = dict()

        self.index = 0
        self.peakindex = 0
        self.WINDOW = re.WINDOW
        self.PEAKWINDOW = 5

        self.running = False
        self.worker = None
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.updatePlots)
        self.timer.start()
        
        self.hasConfChanged = False
        self.connected = False
        
    def setSignals(self):
        self.ui.selec_12.currentIndexChanged.connect(self.leerModoOperacion)
        self.ui.pushButton.clicked.connect(self.leerConfiguracion)
        self.ui.pushButton_2.clicked.connect(self.startWorker)
        self.parent.finished.connect(self.closeEvent)

    def leerConfiguracion(self):
        
        self.conf['AccSamp'] = self.ui.comboBox_acc_sampling.currentIndex()+1
        self.conf['AccSen'] = self.ui.text_acc_sensibity.currentIndex()+1
        self.conf['Modo'] = self.ui.selec_13.currentIndex()+1
        
        if self.running:
            self.hasConfChanged = True
        elif self.connected:
            if self.leerModoOperacion() == 'BMI270':
                re.config_bmi270(self.conf['AccSen'], self.conf['AccSamp'], self.conf['Modo'])
                print(self.conf)
            elif self.leerModoOperacion() == 'BME688':
                re.config_bme688(self.conf['Modo'])
                print("Modo:", self.conf['Modo'])
        else:
            print(self.leerModoOperacion())
            if self.leerModoOperacion() == 'BMI270':
                print(self.conf)
                re.init_connection_bmi270(self.conf['AccSen'], self.conf['AccSamp'], self.conf['Modo'])
            elif self.leerModoOperacion() == 'BME688':
                print("Modo:", self.conf['Modo'])
                re.init_connection_bme688(self.conf['Modo'])
            self.connected = True
        
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.setText("Cambiar configuración")
        self.ui.pushButton.setEnabled(True)
        return self.conf

    def leerModoOperacion(self):
        index = self.ui.selec_12.currentIndex()
        texto = self.ui.selec_12.itemText(index)
        if texto == "BMI270":
            self.ui.onBMI270Select()
        else:
            self.ui.onBME688Select()

        return texto    
        

    def criticalError(self):
        popup = QtWidgets.QMessageBox(parent= self.parent)
        popup.setWindowTitle('Error Critico')
        popup.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        popup.exec()
        return

    def startWorker(self):
        self.toggleFields(False)

        self.running = True
        self.worker = Worker(self.readData, )
        self.threadpool.start(self.worker)

    def stopWorker(self):
        self.toggleFields(True)
        self.running = False

        with self.q.mutex:
                self.q.queue.clear

        self.xlist, self.accx, self.accy, self.accz = [], [], [], []
        self.RMSx, self.RMSy, self.RMSz = [], [], []
        self.FFTx, self.FFTy, self.FFTz = [], [], []
        self.xlistpeaks, self.Peaksx, self.Peaksy, self.Peaksz = [], [], [], []
        self.xlistfft = []

        self.index = 0
        self.peakindex = 0
        
        self.temp = []
        self.humd = []
        self.gas_res = []
        self.pres = []
        self.PeaksTemp = []
        self.PeaksHumd = []
        self.PeaksGas_Res = []
        self.PeaksPres = []

    def updatePlots(self):
        try:
            QtWidgets.QApplication.processEvents()
            while self.running:
                try:
                    data = self.q.get_nowait()
                except queue.Empty:
                    break

                if self.leerModoOperacion() == 'BMI270':
                    self.updatePlotsBMI270(data)
                else:
                    self.updatePlotsBME688(data)
            
            if not self.running:
                self.ui.curve11.setData([], [])
                self.ui.curve12.setData([], [])
                self.ui.curve13.setData([], [])

                self.ui.curve21.setData([], [])
                self.ui.curve22.setData([], [])
                self.ui.curve23.setData([], [])

                self.ui.curve31.setData([], [])
                self.ui.curve32.setData([], [])
                self.ui.curve33.setData([], [])

                self.ui.curve41.setData([], [])
                self.ui.curve42.setData([], [])
                self.ui.curve43.setData([], [])
                self.ui.curve44.setData([], [])

                self.ui.scatter1.setData([], [])
                self.ui.scatter1.setData([], [])
                self.ui.scatter1.setData([], [])
                self.ui.scatter1.setData([], [])
                
        except Exception as e:
            print("ERROR (PLOT):", e)

    def updatePlotsBMI270(self, data):
        try:
            new_accx, new_accy, new_accz, newRMSx, newRMSy, newRMSz, newFFTx, newFFTy, newFFTz, newPeaksx, newPeaksy, newPeaksz = data
        except ValueError:
            print(data)
            raise ValueError
        
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


    def updatePlotsBME688(self, data):
        try:
            temp, humd, gas_res, pres = data
        except ValueError:
            print(data)
            raise ValueError
        
        self.temp += temp
        self.humd += humd
        self.gas_res += gas_res
        self.pres += pres

        self.PeaksTemp = self.updatePeaks(self.temp)
        self.PeaksHumd = self.updatePeaks(self.humd)
        self.PeaksGas_Res = self.updatePeaks(self.gas_res)
        self.PeaksPres = self.updatePeaks(self.pres)

        self.xlist = list(range(len(self.temp)))

        self.ui.curve11.setData(self.xlist, self.temp)
        self.ui.curve22.setData(self.xlist, self.humd)
        self.ui.curve33.setData(self.xlist, self.gas_res)
        self.ui.curve44.setData(self.xlist, self.pres)

        self.ui.scatter1.setData([peak[0] for peak in self.PeaksTemp], [peak[1] for peak in self.PeaksTemp])
        self.ui.scatter2.setData([peak[0] for peak in self.PeaksHumd], [peak[1] for peak in self.PeaksHumd])
        self.ui.scatter3.setData([peak[0] for peak in self.PeaksGas_Res], [peak[1] for peak in self.PeaksGas_Res])
        self.ui.scatter4.setData([peak[0] for peak in self.PeaksPres], [peak[1] for peak in self.PeaksPres])
        
    def updatePeaks(self, data):
        peaks = [(i, data[i]) for i in range(len(data[5:]))]
        peaks.sort(key=lambda x: x[1], reverse=True)
        
        for i in range(6, len(data)):
            val = data[i]
            for j in range(len(peaks)):
                if val > peaks[j][1]:
                    peaks.insert(j, (i, val))
                    break
            peaks = peaks[:5]

        return peaks
            
    def readData(self):
        try:
            QtWidgets.QApplication.processEvents()
            while self.running:
                if self.leerModoOperacion() == 'BMI270':
                    data = re.read_bmi270()
                    if self.hasConfChanged:
                        print(self.conf)
                        re.config_bmi270(self.conf['AccSen'], self.conf['AccSamp'], self.conf['Modo'])
                        self.hasConfChanged = False
                elif self.leerModoOperacion() == 'BME688':
                    data = re.read_bme688()
                    if self.hasConfChanged:
                        print(self.conf)
                        re.config_bme688(self.conf['Modo'])
                        self.hasConfChanged = False
                                  
                if data is None:
                    continue
                self.q.put(data)
                
                

        except Exception as e:
            print("ERROR (WORKER):", e)

    def closeEvent(self, event):
        print('Cerrando el programa')
        self.running = False

    def toggleFields(self, value: bool):
        self.ui.selec_12.setEnabled(value)

        if value:
            self.ui.pushButton_2.setText("Iniciar captación\nde datos")
            self.ui.pushButton_2.clicked.disconnect(self.stopWorker)
            self.ui.pushButton_2.clicked.connect(self.startWorker)
        else:
            self.ui.pushButton_2.setText("Finalizar captación\nde datos")
            self.ui.pushButton_2.clicked.disconnect(self.startWorker)
            self.ui.pushButton_2.clicked.connect(self.stopWorker)


# www.pyshine.com
class Worker(QtCore.QRunnable):
	def __init__(self, function, *args, **kwargs):
		super(Worker, self).__init__()
		self.function = function
		self.args = args
		self.kwargs = kwargs

	@QtCore.pyqtSlot()
	def run(self):

		self.function(*self.args, **self.kwargs)



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