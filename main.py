import sys, os, shutil, shelve
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from MainWindow import Ui_MainWindow
from datetime import datetime

#item_dictionary is a shelve dictionary that contains the name and path for each item
item_dictionary = shelve.open("Item Dictionary")
if not "backup_path" in item_dictionary:
    item_dictionary.update({"backup_path": "No backup path"})
    item_dictionary.sync()

#This makes a zip file that contains a specified directory
#info_tuple[0] contains the backups name, and info_tuple[1] contains the directory being backed up
def backup_dir(info_tuple):
    dest = item_dictionary.get("backup_path")
    #split_dir contains the root_dir, and base_dir
    split_dir = os.path.split(info_tuple[1])
    now = datetime.now()
    file_name = ("{year}-{month}-{day}-{military_time}").format(year = now.strftime("%Y"), month = now.strftime("%m"), day = now.strftime("%d"), military_time = now.strftime("%H%M"))
    dest = os.path.join(dest, info_tuple[0])
    if not os.path.exists(dest):
        os.makedirs(dest)
    dest = os.path.join(dest, file_name)
    shutil.make_archive(dest, "zip", split_dir[0], split_dir[1])

#load_dir extracts a backup of your choosing to replace the folder that is backed up
def load_dir(main_window, info_tuple):
    dir_name = QFileDialog.getOpenFileName(main_window, 'Select file to load', os.path.join(item_dictionary.get("backup_path"), info_tuple[0]))
    dir_name = dir_name[0]
    dest = os.path.split(info_tuple[1])
    dest = dest[0]
    shutil.unpack_archive(dir_name, dest[0])
    
#add_new_dir adds new items to be backed up 
def add_new_dir(main_window):
    while True:
        name, done1 = QInputDialog.getText(main_window, "input dialog", "Enter the name for your backup:")
        if not name in item_dictionary.keys():
            break
        else:
            dlg = QMessageBox(main_window)
            dlg.setWindowTitle("Note")
            dlg.setText("Item already exists")
            dlg.exec()
    if done1:
        backup_path = QFileDialog.getExistingDirectory(main_window, "Choose The Directory")
    if done1 and (len(backup_path) != 0):
        item_dictionary.update({name: backup_path})
        item_dictionary.sync()
        main_window.build_list_widget()
        dir = os.path.join(item_dictionary.get("backup_path"), name)
        if not os.path.exists(dir):
            os.makedirs()

#ListItem is the class that defines the objects put into the ListWidget in the main window
#It displays the name and has buttons to backup the item, load the item, and to edit the item
class ListItem(QWidget):
    def __init__(self, info_tuple, listWidget, build_list_widget):
        super(QWidget, self).__init__()
        self.info_tuple = info_tuple
        self.listWidget = listWidget
        self.build_list_widget = build_list_widget        
        self.horizontalLayout = QHBoxLayout()
        self.checkBox = QCheckBox()
        self.checkBox.setText(info_tuple[0])
        self.horizontalLayout.addWidget(self.checkBox)
        self.backupButton = QPushButton()
        self.backupButton.setText("Backup")
        self.horizontalLayout.addWidget(self.backupButton)
        self.loadButton = QPushButton()
        self.loadButton.setText("Load")
        self.horizontalLayout.addWidget(self.loadButton)
        self.editButton = QPushButton()
        self.editButton.setText("Edit")
        self.horizontalLayout.addWidget(self.editButton)
        self.horizontalLayout.setStretch(0, 1)
        self.setLayout(self.horizontalLayout)
        
        self.backupButton.clicked.connect(lambda: backup_dir(info_tuple))
        self.editButton.clicked.connect(self.edit_info)
        self.loadButton.clicked.connect(lambda: load_dir(self, info_tuple))

    def edit_info(self):
        dlg = EditDialog(self.info_tuple)
        dlg.exec()
        self.build_list_widget()
        
    
#The edit dialog is launched from the edit button in the ListItem class\
#This dialog allows you to edit the path being archived or to remove the item
#When removing the item you have the choice of keeping or removing the backups
class EditDialog(QDialog):
    def __init__(self, info_tuple, parent=None):
        super(QDialog, self).__init__(parent)
        self.setWindowTitle("Edit Item")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 9, -1, -1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.label_2 = QLabel("Name: ")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.itemNameLabel = QLabel(info_tuple[0])
        self.horizontalLayout_3.addWidget(self.itemNameLabel)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QHBoxLayout()
        self.label = QLabel("Path: ")
        self.horizontalLayout_2.addWidget(self.label)
        self.pathDirectoryLabel = QLabel(info_tuple[1])
        self.horizontalLayout_2.addWidget(self.pathDirectoryLabel)
        self.pathChangeButton = QPushButton("Change")
        self.horizontalLayout_2.addWidget(self.pathChangeButton)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        self.horizontalLayout.addWidget(self.buttonBox)
        self.removeDirectoryButton = QPushButton("Remove Directory")
        self.horizontalLayout.addWidget(self.removeDirectoryButton)
        self.horizontalLayout.setSpacing(5)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setLayout(self.verticalLayout)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.info_tuple = info_tuple
        self.pathChangeButton.clicked.connect(lambda: self.change_path_dialog(info_tuple))
        self.removeDirectoryButton.clicked.connect(lambda: self.remove_dir(self.info_tuple))
        
    #This is the method that allows you to change the directory being archived    
    def change_path_dialog(self, info_tuple):
        new_path = QFileDialog.getExistingDirectory(self, "Select New Directory", os.path.split(info_tuple[1])[0])
        if (len(new_path) != 0):
            item_dictionary.update({info_tuple[0]: new_path})
            item_dictionary.sync()
            self.pathDirectoryLabel.setText(item_dictionary.get(info_tuple[0]))
            
    #The method that allows you to remove the directory
    #Has the option to keep or remove the backups
    def remove_dir(self, info_tuple):
        dlg = QMessageBox()
        dlg.setText("Are you sure you would like to delete the item?")
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        status = dlg.exec()
        if status == QMessageBox.StandardButton.Yes:
            item_dictionary.pop(info_tuple[0])
            item_dictionary.sync()
            dlg2 = QMessageBox()
            dlg2.setText("Would you like to delete your backups as well?")
            dlg2.setIcon(QMessageBox.Icon.Warning)
            dlg2.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            status = dlg2.exec()
            if status == QMessageBox.StandardButton.Yes:
                shutil.rmtree(os.path.join(item_dictionary.get("backup_path"), info_tuple[0]))

        

#The class for the main window
class Window(QMainWindow, Ui_MainWindow):
    
    
    def __init__(self, *args, obj=None, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.backupAll.clicked.connect(self.backup_all)
        self.backupSelectedButton.clicked.connect(self.backup_selected)
        self.addNewButton.clicked.connect(lambda: add_new_dir(self))
        self.editBackupPathButton.clicked.connect(self.edit_backup_path)
        self.backup_path = item_dictionary.get("backup_path")
        self.backupPathLabel.setText(self.backup_path)

        self.build_list_widget()
        

    #This method adds all the items to the ListWidget to be displayed.
    def build_list_widget(self):
        self.listWidget.clear()
        tuple_list = []
        for i in item_dictionary:
            if i == "backup_path":
                continue
            k = (i, item_dictionary[i])
            tuple_list.append(k)

        for i in tuple_list:
            list_widget_item = QListWidgetItem()
            list_item = ListItem(i, self.listWidget, self.build_list_widget)
            list_widget_item.setSizeHint(list_item.sizeHint())
            self.listWidget.addItem(list_widget_item)
            self.listWidget.setItemWidget(list_widget_item, list_item)
    
    #This is a getter method that allows information the be gotten from given ListItem
    #This is used for the backup_all and backup_selected methods
    def get_item_info(self, index):
        item = self.listWidget.itemWidget(self.listWidget.item(index))
        return item
    
    #Archives every item in the ListWidget
    def backup_all(self):
        for index in range(self.listWidget.count()):
            item = self.get_item_info(index)
            backup_dir(item.info_tuple, self.backup_path)

    #Archives every item in the list that is checked
    def backup_selected(self):
        for index in range(self.listWidget.count()):
            item = self.get_item_info(index)
            if item.checkBox.isChecked():
                backup_dir(item.info_tuple, item_dictionary.get("backup_path"))
    
    #Method to change the path the backups are stored in
    def edit_backup_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select new backup path")
        if (len(path) != 0):
            item_dictionary.update({"backup_path": path})
            item_dictionary.sync()
            self.backupPathLabel.setText(item_dictionary.get("backup_path"))



        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec()