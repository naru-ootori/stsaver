import sys
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pathlib import Path
from subprocess import run

with open('default.txt', 'r') as f:
    
    conf         = f.readlines()
    default_home = conf[0].replace('\n', '')
    default_path = conf[1].replace('\n', '')
    default_fps  = conf[2].replace('\n', '')

class MainWindow(QMainWindow):
    
    def __init__(self):
    
        super().__init__()
        self.initUI()

    def initUI(self):
    
        self.resize(410, 180)
        self.center()
        self.setWindowTitle('Колобсшиватель 1.1')
        self.setWindowIcon(QIcon('stss_icon.png'))
        
        label_input = QLabel(self)
        label_input.move(10, 1)
        label_input.setFont(QFont('Arial', 11))
        label_input.setText('Input file:')
        
        self.qle_input = QLineEdit(self)
        self.qle_input.setGeometry (10, 30, 310, 25)
                
        self.button_input = QPushButton('Browse', self)
        self.button_input.setFont(QFont('Arial', 11))
        self.button_input.setGeometry(330, 27, 70, 30)
        self.button_input.clicked.connect(self.browse_for_input)

        label_output = QLabel(self)
        label_output.move(10, 60)
        label_output.setFont(QFont('Arial', 11))
        label_output.setText('Output folder:')
                
        self.qle_output = QLineEdit(self)
        self.qle_output.setGeometry (10, 85, 310, 25)
        self.qle_output.setText(default_path)
        
        self.button_output = QPushButton('Browse', self)
        self.button_output.setFont(QFont('Arial', 11))
        self.button_output.setGeometry(330, 82, 70, 30)
        self.button_output.clicked.connect(self.browse_for_output)
        
        label_start = QLabel(self)
        label_start.move(10, 130)
        label_start.setFont(QFont('Arial', 11))
        label_start.setText('Start:')
        
        self.qle_start = QLineEdit(self)
        self.qle_start.setGeometry(48, 131, 40, 25)
        self.qle_start.setInputMask('99:99')
        self.qle_start.setText('00:00')
        
        label_end = QLabel(self)
        label_end.move(95, 130)
        label_end.setFont(QFont('Arial', 11))
        label_end.setText('End:')
        
        self.qle_end = QLineEdit(self)
        self.qle_end.setGeometry (128, 131, 40, 25)
        self.qle_end.setInputMask('99:99')
        self.qle_end.setText('00:00')
        
        label_fps = QLabel(self)
        label_fps.move(175, 130)
        label_fps.setFont(QFont('Arial', 11))
        label_fps.setText('FPS:')
        
        self.qle_fps = QLineEdit(self)
        self.qle_fps.setGeometry (211, 131, 40, 25)
        self.qle_fps.setInputMask('99')
        self.qle_fps.setText(default_fps)
        
        self.button_merge = QPushButton('MP4', self)
        self.button_merge.setFont(QFont('Arial', 10))
        self.button_merge.setGeometry(260, 128, 40, 30)
        self.button_merge.clicked.connect(self.runmmg)
                        
        self.button_stitch = QPushButton('PNG', self)
        self.button_stitch.setFont(QFont('Arial', 10))
        self.button_stitch.setGeometry(310, 128, 40, 30)
        self.button_stitch.clicked.connect(self.runffmpeg)
        
        self.button_decimate = QPushButton('1 / 2', self)
        self.button_decimate.setFont(QFont('Arial', 10))
        self.button_decimate.setGeometry(360, 128, 40, 30)
        self.button_decimate.clicked.connect(self.decimate)
        
        self.progress = QProgressBar(self)
        self.progress.setTextVisible(0)
        self.progress.setGeometry(10, 165, 390, 10)
        self.progress.setMinimum(0)
        self.progress.setMaximum(1)
        self.progress.setValue(0)
     
        self.stamp = '00:00'
     
        self.show()
        
    def center(self):
        
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def browse_for_input(self):
        
        input_file = QFileDialog.getOpenFileName(self, 'Select input file', default_home, 'Video files (*.mkv *.mp4)')
        input_file = str(Path(input_file[0]))
        self.qle_input.setText(input_file)
        
    def browse_for_output(self):
    
        output_folder = QFileDialog.getExistingDirectory(self, 'Select image saving folder')
        output_folder = str(Path(output_folder))
        self.qle_output.setText(output_folder)

    def runffmpeg(self):
    
        source     = Path(self.qle_input.text())
        start      = self.qle_start.text()
        end        = self.qle_end.text()
        t1         = datetime.datetime.strptime(start, '%M:%S')
        t2         = datetime.datetime.strptime(end, '%M:%S')
        duration   = str((t2 - t1).seconds)
        pure_name  = str(Path(source).name)
        pure_name  = pure_name[pure_name.find(']')+2 : pure_name.find('[', pure_name.find(']'))-1]
        self.stamp = pure_name + '-' + t1.strftime('%M%S') + '-' + t2.strftime('%M%S')
        fps        = self.qle_fps.text()
                
        targetfile = Path(self.qle_output.text() + '\\{0}\\{1}-image-%04d.png'.format(self.stamp, source.name[:-4]))
        
        try:
            Path.mkdir(targetfile.parent)
        except OSError as e:
            print ("Error: {0} - {1}.".format(e.filename, e.strerror))
        
        ffm_cl     = 'ffmpeg -hide_banner -ss {0} -t {1} -i \"{2}\" -r {3} \"{4}\"'.format(start, duration, source, fps, targetfile)
        
        self.progress.setValue(0)
        run(ffm_cl)
        self.progress.setValue(1)

    def runmmg(self):
    
        source   = self.qle_input.text()
        target   = self.qle_output.text()
        start    = self.qle_start.text()
        end      = self.qle_end.text()
        fps      = self.qle_fps.text()
        
        tmp_file = Path(target + '\\' + str(Path(source).name))
        
        self.progress.setValue(0)
        
        mkm_cl = 'mkvmerge -o \"{0}\" --split timecodes:{1},{2} --no-audio --no-attachments --no-subtitles --no-global-tags --no-chapters \"{3}\"'.format(tmp_file, start, end, source)
        run(mkm_cl)
        
        fragment1   = Path(target + '\\' + str(Path(source).name)[:-4] + '-001.mkv')
        fragment2   = Path(target + '\\' + str(Path(source).name)[:-4] + '-002.mkv')
        fragment3   = Path(target + '\\' + str(Path(source).name)[:-4] + '-003.mkv')
        temp_video  = Path(target + '\\' + 'temp.h264')
        
        mke_cl      = 'mkvextract tracks \"{0}\" 0:\"{1}\"'.format(fragment2, temp_video)
        run(mke_cl)
        
        final_video = Path(target + '\\' + str(Path(source).name)[:-4] + '-fragment-'+ start.replace(':', '') + '-' + end.replace(':', '') + '.mp4')
                
        m4b_cl      = 'mp4box -add \"{0}\"#video \"{1}\"'.format(temp_video, final_video)
        run(m4b_cl)
        
        try:
            Path.unlink(fragment1)
            Path.unlink(fragment2)
            Path.unlink(fragment3)
            Path.unlink(temp_video)
        except OSError as e:
            print ("Error: {0} - {1}.".format(e.filename, e.strerror))
            
        self.progress.setValue(1)        
        
    def decimate(self):
    
        self.progress.setValue(0)
    
        scan_path = Path(self.qle_output.text() + '\\' + self.stamp)
        file_list = list(scan_path.rglob("*"))
        
        i = 1
        while i < len(file_list) - 1:
            try:
                Path.unlink(file_list[i])
            except OSError as e:
                print ("Error: {0} - {1}.".format(e.filename, e.strerror))    
            i = i + 2
            
        self.progress.setValue(1)
        
app = QApplication(sys.argv)
mw  = MainWindow()
app.exec_()