import sys
from PyQt6.QtWidgets import QInputDialog, QApplication, QWidget,  QGridLayout, QListWidget, QPushButton, QLabel, QMessageBox, QLineEdit
from cfg_handler import cfg_handler, path_cfg_handler
#based on https://www.pythontutorial.net/pyqt/pyqt-qlistwidget/

class PopupWindow(QWidget):
    def __init__(self, brush0, brush1, brush1_index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg1 = cfg_handler()

        self.setWindowTitle('Brush Comparison')
        #self.setWindowIcon(QIcon('./assets/wishlist.png'))
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
        
        label4 = QLabel(self)
        label4.setText(f'{brush1}')
        layout.addWidget(label4, 2, 2)
        
        
        #qlists
        self.curr_brushlist_details = QListWidget(self)
        self.curr_brushlist_details.addItems(self.cfg1.get_brush_details(self.cfg1.brush2cfg, None, brush1_index))
        layout.addWidget(self.curr_brushlist_details, 4, 2, 4, 1)
        
        self.default_brushlist_details = QListWidget(self)
        self.default_brushlist_details.addItems(self.cfg1.get_brush_details(self.cfg1.defaultcfg, self.cfg1.default_brushes, brush0))
        layout.addWidget(self.default_brushlist_details, 4, 0, 4, 1)
 
        #self.show()

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #instantiate cfg handler
        self.cfg1 = cfg_handler()
        
        #pop up window
        self.w = None

        self.setWindowTitle('Brush Config Manager: Main Window')
        #self.setWindowIcon(QIcon('./assets/wishlist.png'))
        self.setGeometry(100, 100, 1080, 480)

        layout = QGridLayout(self)
        self.setLayout(layout)
        
        #qlabels
        label = QLabel(self)
        label.setText("Default Brushes:")
        layout.addWidget(label, 0, 0)
        
        label2 = QLabel(self)
        label2.setText("My Brushes:")
        layout.addWidget(label2, 0, 2)
        
        label3 = QLabel(self)
        label3.setText("My Brush Groups:\n*Attribute of Brushes from 'My Brushes'")
        layout.addWidget(label3, 0, 4)
        
        label3_0 = QLabel(self)
        label3_0.setText("A group 'New Brushes' will automatically \nbe added on 'Import' if it doesn't exist.")
        layout.addWidget(label3_0, 1, 4)
        
        label3_1 = QLabel(self)
        label3_1.setText("Brushes selected from 'My Brushes' can\nbe moved into a selected 'Brush Group'.")
        layout.addWidget(label3_1, 2, 4)
        
        label3_2 = QLabel(self)
        label3_2.setText("Brushes selected from 'Default Brushes' can\nbe imported into a selected 'Brush Group'.")
        layout.addWidget(label3_2, 3, 4)
        
        self.label4 = QLabel(self)
        self.label4.setText(f"Target Group:\n None Selected")
        layout.addWidget(self.label4, 0, 6)
        
        self.label5 = QLabel(self)
        self.label5.setText(f'Last Selected:\nNone')
        layout.addWidget(self.label5, 3, 0)
        
        self.label5_1 = QLabel(self)
        self.label5_1.setText(f'Last Selected:\nNone')
        layout.addWidget(self.label5_1, 3, 2)

        #qlist widgets
        self.curr_brushlist = QListWidget(self)
        self.curr_brushlist.addItems(self.cfg1.current_brushes_list)
        layout.addWidget(self.curr_brushlist, 4, 2, 4, 1)
        self.curr_brushlist.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        self.default_brushlist = QListWidget(self)
        self.default_brushlist.addItems(self.cfg1.default_brushes.keys())
        layout.addWidget(self.default_brushlist, 4, 0, 4, 1)
        self.default_brushlist.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        self.grouplist = QListWidget(self)
        self.grouplist.addItems([f'{self.cfg1.brush_groups[key]}: {key}' for key in self.cfg1.brush_groups])
        layout.addWidget(self.grouplist, 4, 4, 4, 1)
        
        self.brushes_in_grouplist = QListWidget(self)
        self.brushes_in_grouplist.addItems(['Select a Brush Group',])
        layout.addWidget(self.brushes_in_grouplist, 1, 6, 4, 1)

        # create buttons
        import_button = QPushButton('Import Selected')
        import_button.clicked.connect(self.import_selected)

        deselect_default_button = QPushButton('Deselect')
        deselect_default_button.clicked.connect(self.deselect_from_default)
        
        deselect_current_button = QPushButton('Deselect')
        deselect_current_button.clicked.connect(self.deselect_from_current)

        remove_button = QPushButton('Delete Selected')
        remove_button.clicked.connect(self.remove)

        self.details_button = QPushButton('Open Brush Compare')
        self.details_button.clicked.connect(self.open_popup)
        
        move_to_group_btn = QPushButton('Send Selected Brushes\n to Target Group')
        move_to_group_btn.clicked.connect(self.send_brushes)
        
        add_group_btn = QPushButton('Add Brush Group')
        add_group_btn.clicked.connect(self.add_brush_group)
        
        delete_group_btn = QPushButton('Deleted Selected Group')
        delete_group_btn.clicked.connect(self.delete_brush_group)
        
        #misc triggers
        self.grouplist.itemClicked.connect(self.show_brushes_in_group)
        self.curr_brushlist.itemClicked.connect(self.update_last_selected_brush_current)
        self.default_brushlist.itemClicked.connect(self.update_last_selected_brush_default)
        
        #btn layout
        layout.addWidget(import_button, 1, 0)
        
        layout.addWidget(deselect_default_button, 2, 0)
        
        
        layout.addWidget(remove_button, 1, 2)
        
        layout.addWidget(deselect_current_button, 2, 2)
        
        
        layout.addWidget(self.details_button, 3, 3)
        
        layout.addWidget(move_to_group_btn, 1, 5)
        
        layout.addWidget(add_group_btn, 2, 5)
        
        layout.addWidget(delete_group_btn, 3, 5)
        # show the window
        #self.show()

    def import_selected(self):
        import_list = [x.text() for x in self.default_brushlist.selectedItems() 
                       if x.text() not in [self.cfg1.brush2cfg[section]['name'] for section in self.cfg1.brush2cfg.sections()[1:]]]
        
        #update group list
        if self.cfg1.import_brushes(import_list, str(self.grouplist.currentRow())):
            self.grouplist.addItem(f'{self.cfg1.brush_groups['New Brushes']}: {'New Brushes'}')
            
        self.curr_brushlist.clear()
        self.curr_brushlist.addItems(self.cfg1.current_brushes_list)
        
        self.show_brushes_in_group()
        
        
    def remove(self):
        del_list = [self.curr_brushlist.row(x) for x in self.curr_brushlist.selectedItems()]
        
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
        self.label5.setText(f'Last Selected:\n{self.default_brushlist.currentItem().text()}')
        
    def update_last_selected_brush_current(self):
        self.label5_1.setText(f'Last Selected:\n{self.curr_brushlist.currentItem().text()}')
            

    def open_popup(self):
        if self.w is None:
            if self.default_brushlist.currentItem() != None:
                brush0 = self.default_brushlist.currentItem().text()
            else:
                brush0 = 'None Selected'
                
            if self.curr_brushlist.currentRow() != -1:
                brush1 = self.cfg1.current_brushes_list[self.curr_brushlist.currentRow()]#self.curr_brushlist.currentItem().text()
            else:
                brush1 = 'None Selected'
                
            self.w = PopupWindow(brush0, brush1, str(self.curr_brushlist.currentRow()))
            self.w.show()
            self.details_button.setText('Close Brush Compare')

        else:
            self.w = None 
            self.details_button.setText('Open Brush Compare')
            
    def send_brushes(self):
        brush_list = []
        for itm in self.curr_brushlist.selectedItems():
            brush_list.append(itm.text())
        
        self.cfg1.set_brush_group(brush_list, str(self.grouplist.currentRow()))
        self.show_brushes_in_group()
        
    def show_brushes_in_group(self):
        #update Q list
        self.brushes_in_grouplist.clear()
        str_list = self.cfg1.get_brush_names_from_group(str(self.grouplist.currentRow()))
        if self.grouplist.currentRow() == -1:
            str_list = []
        if str_list == []:
            str_list.append('No Brushes')
        self.brushes_in_grouplist.addItems(str_list)
        
        #update label
        if self.grouplist.currentItem() != None:
            self.label4.setText(f"Target Group:\n {self.grouplist.currentItem().text()}")
            
    def add_brush_group(self):
        text, ok = QInputDialog.getText(self, 'Add New Brush Group', 'Name:')
        if ok and text:
            self.cfg1.add_group(text)
        #reset grouplist
        self.grouplist.clear()
        self.grouplist.addItems([f'{self.cfg1.brush_groups[key]}: {key}' for key in self.cfg1.brush_groups])
            
    def delete_brush_group(self):
        self.cfg1.delete_group(str(self.grouplist.currentRow()))
        #reset grouplist
        self.grouplist.clear()
        self.grouplist.addItems([f'{self.cfg1.brush_groups[key]}: {key}' for key in self.cfg1.brush_groups])
        self.brushes_in_grouplist.clear()
        
        #reset my brush list
        self.curr_brushlist.clear()
        self.curr_brushlist.addItems(self.cfg1.current_brushes_list)
        
        
class ini_window(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = None
        self.cfg0 = path_cfg_handler()
        
        self.setWindowTitle('Brush Config Manager: Path Selection')
        #self.setWindowIcon(QIcon('./assets/wishlist.png'))
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
        label2.setText('Suggested: C:\\Users\\[your username]\\AppData\\Local\\Medibang\\CloudAlpaca\n\nDemo Path: src\\demo')
        layout.addWidget(label2, 3, 0)
        
        self.launch_btn = QPushButton('Launch Main Program')
        self.launch_btn.clicked.connect(self.launch_program)
        layout.addWidget(self.launch_btn, 1, 1)
        
        self.label3 = QLabel()
        self.label3.setText(f'Current Path: {self.cfg0.get_curr_path()}')
        layout.addWidget(self.label3, 2, 0)
        
        self.show()
        
    def launch_program(self):
        if self.pathTextBox.text() != '':#set new path if provided
            self.label3.setText(f'Current Path: {self.pathTextBox.text()}')
            self.cfg0.set_curr_path(self.pathTextBox.text())
            
        if self.main_window is None:
            self.main_window = MainWindow()
            self.main_window.show()
            self.launch_btn.setText('Un-Launch Main Progam')
        else:
            self.main_window = None
            self.launch_btn.setText('Launch Main Program')
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ini_window()
    sys.exit(app.exec())