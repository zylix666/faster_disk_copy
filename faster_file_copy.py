import sys
import time
import argparse
import os
import shutil
from random import shuffle
from multiprocessing.dummy import Pool as ThreadPool


parser = argparse.ArgumentParser()

from PyQt5.QtCore import QThread, pyqtSignal

from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton, QVBoxLayout, QMessageBox)

thread_number = 1

source_path = ""
destination_path = ""

class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int, int)
    copyCompleted = pyqtSignal(int, int)
    
    def thread_id(self, thread_id):
        self.ID = thread_id
        print("I am thread ID : ", self.ID)
        
    def setWorkLoad(self, file_list_):
        self.file_list = file_list_
        self.file_list_len = len(file_list_)
        
    def run(self):
        print("run...")
        #count = 0
        percentage_count = 0
        start_time = time.time()
        while len(self.file_list) > 0:
            filename = self.file_list.pop()
            shutil.copyfile(source_path+filename, destination_path+filename)
            #count +=1
            percentage_count = 100-((len(self.file_list)/self.file_list_len)*100)
            self.countChanged.emit(self.ID, percentage_count)
        elapsed_time = time.time() - start_time
        self.copyCompleted.emit(self.ID, elapsed_time)

class Actions(QDialog):
    """
    Simple dialog that consists of a Progress Bar and a Button.
    Clicking on the button results in the start of a timer and
    updates the progress bar.
    """
    def __init__(self):
        super().__init__()
        self.left = 50
        self.top = 50
        self.width = 640
        self.height = 480
        self.initUI()
        self.elapsed_time_dict = {}
        
    def initUI(self):
        self.setWindowTitle('Faster File copy - %d threads'%thread_number)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch(1)
        self.progressbars = []

        for i in range(thread_number):
            prog_bar = QProgressBar(self)
            self.vbox.addWidget(prog_bar)
            self.progressbars.append(prog_bar)
            
        self.button = QPushButton('Start', self)
        
        self.vbox.addWidget(self.button)
        self.button.move(0, 30)
        self.setLayout(self.vbox)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

        self.button.clicked.connect(self.onButtonClick)

    def set_FileData(self, file_lists_):
	    # A list contains splited file list
        self.file_list_queue = file_lists_
        for i in range(thread_number):
            #self.progressbars[i].setMaximum(len(self.file_list_queue[i])) 
            self.progressbars[i].setMaximum(100)
        self.thread_list = []
        for i in range(thread_number):
            copy_worker = External()
            copy_worker.setWorkLoad(self.file_list_queue[i])
            copy_worker.thread_id(i)
            copy_worker.countChanged.connect(self.onCountChanged)
            copy_worker.copyCompleted.connect(self.onCopyCompleted)
            self.thread_list.append(copy_worker)
            
    def onButtonClick(self):
        for worker in self.thread_list:
            print("worker ready.....go!")
            worker.start()

    def onCountChanged(self, ID, count):
        self.progressbars[ID].setValue(count)

    def onCopyCompleted(self, ID, elapsed_time):
        self.elapsed_time_dict[ID] = elapsed_time
        #print("Thread ID %d finished with %d sec. " % (self.elapsed_time_dict[ID], elapsed_time))
        Total_elapsed_time = 0
        if(len(self.elapsed_time_dict) == thread_number):
            for et in self.elapsed_time_dict.values():
                Total_elapsed_time += et
            if thread_number > 2 : 
                div_base = thread_number-1
            else:
                div_base = thread_number
            reply = QMessageBox.information(self, "All file copied","Total copy time : " + str(Total_elapsed_time/div_base) + " seconds.",
                                    QMessageBox.Ok)

def split(arr, size):
    arrs = []
    #print("split---------------", size)
    if size == len(arr):
        arrs.append(arr)
        print("no segment : ", len(arrs))
        return arrs
    
    while len(arr) > size:
        pice = arr[:size]
        #print("pice len: ", len(pice))
        arrs.append(pice)
        #print("arrs len : ", len(arrs))
        arr   = arr[size:]
        #print("arr left size : ", len(arr))
    if(len(arr) > 0):
        arrs.append(arr)
    print("split ++++++++",len(arrs))
    return arrs

def split_list(file_list, segment):
    if segment == 1:
        return split(file_list, len(file_list))
    
    if (len(file_list)%segment) !=0:
        splited_lists = split(file_list, (len(file_list)//segment)-1)
    else:
        splited_lists = split(file_list, len(file_list)//segment)
    return splited_lists

if __name__ == "__main__":
    parser.add_argument("-src", "--src_dir", dest = "src_dir", default = ".\\test_256", help="source of dataset")
    parser.add_argument("-dst", "--dst_dir", dest = "dst_dir", default = ".\\copy_dst", help="destination of dataset")
    parser.add_argument("-sec", "--section",dest = "section", default = "1", help="The threads for copying", type=int)

    args = parser.parse_args()

    #depends on how many section to create the threads
    thread_number = args.section
    
    source_path = args.src_dir + "\\"
    destination_path = args.dst_dir +"\\"
    
    file_list = []
    for _,_,filenames in os.walk(args.src_dir):
        file_list.extend(filenames)
    
    shuffle(file_list)
    
    print("thread_number", thread_number)
    local_file_list = split_list(file_list, thread_number)
    
    print("file_list_queue", len(local_file_list))
    for arr in local_file_list:
        print("file list len : ", len(arr))
    if (len(local_file_list) > thread_number):
        thread_number += len(local_file_list)-thread_number
	
    app = QApplication(sys.argv)
    window = Actions()
    window.set_FileData(local_file_list)
    sys.exit(app.exec_())