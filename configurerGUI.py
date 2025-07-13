import sys
from PyQt6.QtWidgets import QInputDialog, QApplication, QWidget, QGridLayout, QListWidget, QPushButton, QLabel, QMessageBox, QLineEdit
from PyQt6.QtGui import QIcon
from cfg_handler import cfg_handler, path_cfg_handler
#based on https://www.pythontutorial.net/pyqt/pyqt-qlistwidget/

class PopupWindow(QWidget):
    def __init__(self, brush0, brush1, brush1_index, defaultcfg, brush2cfg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg1 = cfg_handler()

        self.setWindowTitle('Brush Comparison')
        self.setWindowIcon(QIcon('./src/brushcfg_icon2.ico'))
        self.setGeometry(100, 100, 720, 400)

        layout = QGridLayout(self)
        self.setLayout(layout)
        
        #qlabels
        label = QLabel(self)
        label.setText("Comparing Brushes that were last clicked from\n'Default Brushes' and 'My Brushes'.\n\nClick 'Compare Brushes' button on main window to reset.")
        layout.addWidget(label)
        
        label1 = QLabel(self)
        label1.setText("From Default Brushes:")
        layout.addWidget(label1, 1, 0)
        
        label2 = QLabel(self)
        label2.setText("From My Brushes:")
        layout.addWidget(label2, 1, 2)
        
        label3 = QLabel(self)
        label3.setText(f'{brush0}')
        layout.addWidget(label3, 2, 0)
        
        target_group_name_label = QLabel(self)
        target_group_name_label.setText(f'{brush1}')
        layout.addWidget(target_group_name_label, 2, 2)
        
        
        #qlists
        self.curr_brushlist_details = QListWidget(self)
        self.curr_brushlist_details.addItems(self.cfg1.get_brush_details(brush2cfg, None, brush1_index))
        layout.addWidget(self.curr_brushlist_details, 4, 2, 4, 1)
        
        self.default_brushlist_details = QListWidget(self)
        self.default_brushlist_details.addItems(self.cfg1.get_brush_details(defaultcfg, self.cfg1.default_brushes_dict, brush0))
        layout.addWidget(self.default_brushlist_details, 4, 0, 4, 1)
 
        #self.show()

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #instantiate cfg handler
        self.cfg1 = cfg_handler()
        
        #pop up window
        self.w = None
        
        self.filter_active = False
        self.hash = None
        
        self.file_deletion_en = False

        self.setWindowTitle('Brush Config Manager: Main Window')
        self.setWindowIcon(QIcon('./src/brushcfg_icon2.ico'))
        self.setGeometry(100, 100, 1080, 480)

        layout = QGridLayout(self)
        self.setLayout(layout)
        
        #qlabels--------------------------------------------------------------------------------------------
        label = QLabel(self)
        label.setText("Default Brushes:")
        layout.addWidget(label, 0, 0)
        
        label2 = QLabel(self)
        label2.setText("My Brushes:")
        layout.addWidget(label2, 0, 2)
        
        label3 = QLabel(self)
        label3.setText("My Brush Groups:\n*Attribute of Brushes from 'My Brushes'")
        layout.addWidget(label3, 0, 4)
        
        # label3_0 = QLabel(self)
        # label3_0.setText("A group 'New Brushes' will automatically \nbe added on 'Import' if it doesn't exist.")
        # layout.addWidget(label3_0, 1, 4)
        
        # label3_1 = QLabel(self)
        # label3_1.setText("Brushes selected from 'My Brushes' can\nbe moved into a selected 'Brush Group'.")
        # layout.addWidget(label3_1, 2, 4)
        
        # label3_2 = QLabel(self)
        # label3_2.setText("Brushes selected from 'Default Brushes' can\nbe imported into a selected 'Brush Group'.")
        # layout.addWidget(label3_2, 3, 4)
        
        self.target_group_name_label = QLabel(self)
        self.target_group_name_label.setText(f"Target Group:\n-1: Unassigned Brushes ")
        layout.addWidget(self.target_group_name_label, 4, 4)
        
        brushes_in_brushlist_label = QLabel(self)
        brushes_in_brushlist_label.setText(f"Brushes in Target Group:")
        layout.addWidget(brushes_in_brushlist_label, 4, 5)
        
        self.default_brushes_last_sel_label = QLabel(self)
        self.default_brushes_last_sel_label.setText(f'Last Selected:\nNone')
        layout.addWidget(self.default_brushes_last_sel_label, 3, 0)
        
        self.my_brushes_last_sel_label = QLabel(self)
        self.my_brushes_last_sel_label.setText(f'Last Selected:\nNone')
        layout.addWidget(self.my_brushes_last_sel_label, 3, 2)

        #qlist widgets-----------------------------------------------------------------------------------------------------
        self.curr_brushlist = QListWidget(self)
        self.curr_brushlist.addItems(self.cfg1.current_brushes_list)
        layout.addWidget(self.curr_brushlist, 5, 2, 6, 1)
        self.curr_brushlist.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        self.default_brushlist = QListWidget(self)
        self.default_brushlist.addItems(self.cfg1.default_brushes_dict.keys())
        layout.addWidget(self.default_brushlist, 5, 0, 6, 1)
        self.default_brushlist.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        self.grouplist = QListWidget(self)
        self.grouplist.addItems(self.cfg1.get_formatted_brushgroup_strlist())
        layout.addWidget(self.grouplist, 6, 4, 4, 1)
        
        self.brushes_in_grouplist = QListWidget(self)
        self.brushes_in_grouplist.addItems(['Select a Brush Group',])
        layout.addWidget(self.brushes_in_grouplist, 5, 5, 4, 1)

        #qpushbuttons-------------------------------------------------------------------------------
        import_button = QPushButton('Import Selected')
        import_button.clicked.connect(self.import_selected)
        layout.addWidget(import_button, 1, 0)

        deselect_default_button = QPushButton('Deselect All')
        deselect_default_button.clicked.connect(self.deselect_from_default)
        layout.addWidget(deselect_default_button, 4, 0)
        
        deselect_current_button = QPushButton('Deselect All')
        deselect_current_button.clicked.connect(self.deselect_from_current)
        layout.addWidget(deselect_current_button, 4, 2)

        remove_button = QPushButton('Delete Selected')
        remove_button.clicked.connect(self.remove)
        layout.addWidget(remove_button, 1, 2)
        
        self.file_deletion_en_btn = QPushButton('Enable File Deletion')
        self.file_deletion_en_btn.clicked.connect(self.toggle_file_deletion)
        layout.addWidget(self.file_deletion_en_btn, 2, 2)
        
        select_unassigned_btn = QPushButton('Selected Unnassigned Brushes')
        select_unassigned_btn.clicked.connect(self.select_unassigned)
        layout.addWidget(select_unassigned_btn, 5, 4)

        self.details_button = QPushButton('Open Brush Compare')
        self.details_button.clicked.connect(self.open_popup)
        layout.addWidget(self.details_button, 3, 3)
        
        self.filter_by_group_btn = QPushButton("[Filter] 'My Brushes' by [Target Group: -1]")
        self.filter_by_group_btn.clicked.connect(self.filter_by_group)
        layout.addWidget(self.filter_by_group_btn, 4, 3)
        
        self.move_to_group_btn = QPushButton('[Move] Selected Brushes to [Target Group: -1]')
        self.move_to_group_btn.clicked.connect(self.move_brushes)
        layout.addWidget(self.move_to_group_btn, 5, 3)
        
        add_group_btn = QPushButton('Add Brush Group')
        add_group_btn.clicked.connect(self.add_brush_group)
        layout.addWidget(add_group_btn, 1, 4)
        
        delete_group_btn = QPushButton('Deleted Target Group')
        delete_group_btn.clicked.connect(self.delete_brush_group)
        layout.addWidget(delete_group_btn, 2, 4)
        
        rename_group_btn = QPushButton('Rename Target Group')
        rename_group_btn.clicked.connect(self.rename_brush_group)
        layout.addWidget(rename_group_btn, 3, 4)
        
        color = 'ff0000'
        save_btn = QPushButton('[!] Overwrite Config [!]')
        save_btn.setStyleSheet(f'color: #{color};')
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn, 0, 5)
        
        #misc triggers----------------------------------------------------------------------------------------------
        self.grouplist.itemClicked.connect(self.show_brushes_in_group)
        self.curr_brushlist.itemClicked.connect(self.update_last_selected_brush_current)
        self.default_brushlist.itemClicked.connect(self.update_last_selected_brush_default)
        
        self.show_brushes_in_group()
        
    #-------------------------------brush related functions--------------------------------------------------------------------
    def import_selected(self):
        #only import brushes that don't already exist in my brushes
        import_list = [x.text() for x in self.default_brushlist.selectedItems()]
        #update group list
        if self.cfg1.import_brushes(import_list, str(self.grouplist.currentRow())):#True if New Brushes group doesn't exist
            self.refresh_grouplist()
          
        self.refresh_curr_brushlist(self.cfg1.current_brushes_list)
        self.show_brushes_in_group()
        
        self.filter_active = False
        self.hash = None
        
        
    def remove(self):
        if self.hash == None:
            del_list = [self.curr_brushlist.row(x) for x in self.curr_brushlist.selectedItems()]
        else:
            del_list = [self.hash[self.curr_brushlist.row(x)] for x in self.curr_brushlist.selectedItems()]
        
        #print(del_list)
        self.cfg1.delete_brushes(del_list)
        
        for x in self.curr_brushlist.selectedItems():
            self.curr_brushlist.takeItem(self.curr_brushlist.row(x))
            del x
        
        self.show_brushes_in_group()
        
    def deselect_from_default(self):
        for x in self.default_brushlist.selectedItems():
            x.setSelected(False)
            
    def deselect_from_current(self):
        for x in self.curr_brushlist.selectedItems():
            x.setSelected(False)
            
    def update_last_selected_brush_default(self):
        self.default_brushes_last_sel_label.setText(f'Last Selected:\n{self.default_brushlist.currentItem().text()}')
        
    def update_last_selected_brush_current(self):
        self.my_brushes_last_sel_label.setText(f'Last Selected:\n{self.curr_brushlist.currentItem().text()}')
            
    def toggle_file_deletion(self):
        if not self.file_deletion_en:
            msg = QMessageBox(window)
            msg.setWindowTitle("Warning")
            msg.setText("Enabling file deletion will delete brush scripts and bitmaps from your local directory in addition to removing them from the config files.\n\nThis software only has replacement files for the brushes in 'Default Brushes'.")
            msg.exec()
            self.file_deletion_en_btn.setText('Disable File Deletion')
            self.file_deletion_en = True
        else:
            self.file_deletion_en = False
            self.file_deletion_en_btn.setText('Enable File Deletion')
            
    def save(self):
        self.cfg1.save_changes(self.file_deletion_en)
        msg = QMessageBox(window)
        msg.setWindowTitle("Config Saved")
        msg.setText("Close all windows and open Medibang to confirm changes.")
        msg.exec()
    
    def open_popup(self):
        if self.w is None:
            if self.default_brushlist.currentItem() != None:
                brush0 = self.default_brushlist.currentItem().text()
            else:
                brush0 = 'None Selected'
                
            if self.curr_brushlist.currentRow() != -1:
                if self.hash == None:
                    key = self.curr_brushlist.currentRow()
                else:
                    key = self.hash[self.curr_brushlist.currentRow()]
                brush1 = self.cfg1.current_brushes_list[key]
                brush1_index = str(key)
            else:
                brush1 = 'None Selected'
                brush1_index = '0'
                
            self.w = PopupWindow(brush0, brush1, brush1_index, self.cfg1.defaultcfg, self.cfg1.brush2cfg)
            self.w.show()
            self.details_button.setText('Close Brush Compare')

        else:
            self.w = None 
            self.details_button.setText('Open Brush Compare')
            
            
    #----------------------------------------------brush group related functions------------------------------------------
    def move_brushes(self):
        brush_list = []
        if self.hash == None:
            brush_list = [self.curr_brushlist.row(x) for x in self.curr_brushlist.selectedItems()]
        else:
            brush_list = [self.hash[self.curr_brushlist.row(x)] for x in self.curr_brushlist.selectedItems()]
        
        self.cfg1.set_brush_group(brush_list, str(self.grouplist.currentRow()))
        self.show_brushes_in_group() #update brushes in group
        if self.filter_active:#update hash and my brushes
            for selected_item in self.curr_brushlist.selectedItems():
                self.hash.pop(self.curr_brushlist.row(selected_item))
                self.curr_brushlist.takeItem(self.curr_brushlist.row(selected_item))
                del selected_item
        else:
            self.refresh_curr_brushlist(self.cfg1.current_brushes_list)
                
    def refresh_grouplist(self):
        self.grouplist.clear()
        self.grouplist.addItems(self.cfg1.get_formatted_brushgroup_strlist())
        
    def refresh_curr_brushlist(self, str_list):
        self.curr_brushlist.clear()
        self.curr_brushlist.addItems(str_list)

        
    def show_brushes_in_group(self):
        #update Q list
        self.brushes_in_grouplist.clear()
        str_list = self.cfg1.get_brush_names_from_group(str(self.grouplist.currentRow()))

        self.brushes_in_grouplist.addItems(str_list)
        
        #update label
        if self.grouplist.currentItem() != None:
            self.target_group_name_label.setText(f"Target Group:\n {self.grouplist.currentItem().text()}")
            
        #update button text
        if not self.filter_active:
            self.filter_by_group_btn.setText(f"[Filter] 'My Brushes' by [Target Group: {self.grouplist.currentRow()}]")
        self.move_to_group_btn.setText(f"[Move] Selected Brushes to [Target Group: {self.grouplist.currentRow()}]")
            
    def add_brush_group(self):
        text, ok = QInputDialog.getText(self, 'Add New Brush Group', 'Name:')
        if ok and text:
            self.cfg1.add_group(text)
        #reset grouplist
        self.refresh_grouplist()
        
    def delete_brush_group(self):
        self.cfg1.delete_group(str(self.grouplist.currentRow()))
        #reset grouplist
        self.refresh_grouplist()
        self.brushes_in_grouplist.clear()
        
        #reset my brush list
        self.refresh_curr_brushlist(self.cfg1.current_brushes_list)
        
        self.hash = None
        
    def rename_brush_group(self):
        if self.grouplist.currentItem() != None:
            text, ok = QInputDialog.getText(self, f'Renaming Group {self.grouplist.currentItem().text()}', 'New Name:')
            if ok and text:
                self.cfg1.rename_group(str(self.grouplist.currentRow()), text)
 
                #update grouplist
                self.grouplist.currentItem().setText(self.cfg1.get_formatted_brushgroup_strlist()[self.grouplist.currentRow()])
                
                #set target group name
                self.target_group_name_label.setText(f"Target Group:\n {self.grouplist.currentItem().text()}")
                
    def filter_by_group(self):
        if self.filter_active:
            self.filter_by_group_btn.setText(f"[Filter] 'My Brushes' by [Target Group: {self.grouplist.currentRow()}]")
            self.refresh_curr_brushlist(self.cfg1.current_brushes_list)
            self.hash = None
            self.filter_active = False
        else:
            self.filter_by_group_btn.setText('Clear Group Filter')
            self.refresh_curr_brushlist(self.cfg1.get_filtered_currbrush_list(str(self.grouplist.currentRow())))
            self.hash = self.cfg1.get_relative_hash(str(self.grouplist.currentRow()))
            self.filter_active = True
            
    def select_unassigned(self):
        self.grouplist.setCurrentRow(-1)
        self.target_group_name_label.setText(f"Target Group:\n{self.grouplist.currentRow()}: Unassigned Brushes ")
        self.show_brushes_in_group()
        
class ini_window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = None
        self.cfg0 = path_cfg_handler()
        
        self.setWindowTitle('Brush Config Manager: Path Selection')
        self.setWindowIcon(QIcon('./src/brushcfg_icon2.ico'))
        self.setGeometry(100, 100, 400, 100)

        layout = QGridLayout(self)
        self.setLayout(layout)
        
        #qlabels
        label = QLabel(self)
        label.setText("Input Path to Medibang Config File:")
        layout.addWidget(label, 0, 0)
        
        self.pathTextBox = QLineEdit(self)
        #self.pathTextBox.textChanged.connect(self.updatepath)
        layout.addWidget(self.pathTextBox, 1, 0)

        label2 = QLabel()
        label2.setText('Typical Path: C:\\Users\\[your username]\\AppData\\Local\\Medibang\\CloudAlpaca\n\nDemo Path: src\\demo')
        layout.addWidget(label2, 3, 0)
        
        self.launch_btn = QPushButton('Launch Main Window')
        self.launch_btn.clicked.connect(self.launch_program)
        layout.addWidget(self.launch_btn, 1, 1)
        
        self.label3 = QLabel()
        self.label3.setText(f'Current Path: {self.cfg0.get_curr_path()}\n')
        layout.addWidget(self.label3, 2, 0)
        
        self.show()
        
    def launch_program(self):
        if self.pathTextBox.text() != '':#set new path if provided
            self.label3.setText(f'Current Path: {self.pathTextBox.text()}')
            self.cfg0.set_curr_path(self.pathTextBox.text())
            
        if self.main_window is None:
            self.main_window = MainWindow()
            self.main_window.show()
            self.launch_btn.setText('Un-Launch Main Window')
            self.hide()
        else:
            self.main_window = None
            self.launch_btn.setText('Launch Main Window')
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ini_window()
    sys.exit(app.exec())