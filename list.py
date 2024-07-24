import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QListWidgetItem,
                             QVBoxLayout, QPushButton, QWidget, QTabWidget, QLineEdit,QStyledItemDelegate)
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QColor
class AlternatingColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Apply alternating colors
        if index.row() % 2 == 0:
            painter.fillRect(option.rect, QColor('#38dba4'))
        else:
            painter.fillRect(option.rect, QColor('#dc7598'))
        
        # Draw the default item display
        super().paint(painter, option, index)
class ListManager(QObject):
    request_update = pyqtSignal()  # Add this line to your existing signals
    item_moved = pyqtSignal(int, str, int, str)  # old_index, old_list, new_index, new_list
    item_renamed = pyqtSignal(int, str, str)     # index, list_name, new_value

    def __init__(self, list1, list2, display_key, item_moved_handler=None, item_renamed_handler=None):
        super().__init__()
        self.list1 = list1
        self.list2 = list2
        self.display_key = display_key
        if item_moved_handler:
            self.item_moved.connect(item_moved_handler)
        if item_renamed_handler:
            self.item_renamed.connect(item_renamed_handler)
    def add_item(self, list_name, item):
        if list_name == 'list1':
            self.list1.append(item)
        else:
            self.list2.append(item)
        self.request_update.emit()
    def rename_item(self, list_name, index, new_name):
        lst = self.list1 if list_name == 'list1' else self.list2
        if index < len(lst):
            lst[index][self.display_key] = new_name
            self.request_update.emit()
    def transfer_first_element(self):
        if self.list1:  # Check if list1 is not empty
            element = self.list1.pop(0)  # Remove the first element from list1
            self.list2.append(element)  # Append the removed element to list2
            self.request_update.emit()  # Assuming there's some update mechanism
        else:
            print("List1 is empty, no elements to transfer.")
            
    def remove_item(self, list_name, index):
        if list_name == 'list1' and index < len(self.list1):
            del self.list1[index]
        elif list_name == 'list2' and index < len(self.list2):
            del self.list2[index]
        self.request_update.emit()
    def get_item(self, list_name, index):
        if list_name == 'list1' and index < len(self.list1):
            return self.list1[index]
        elif list_name == 'list2' and index < len(self.list2):
            return self.list2[index]
        
    def move_item(self, source, target, index):
        if index < 0 or index >= len(source):
            return
        item = source.pop(index)
        target.append(item)
        self.item_moved.emit(index, 'list1' if source is self.list1 else 'list2',
                             len(target)-1, 'list2' if target is self.list2 else 'list1')

    def move_up_down(self, lst, index, direction):
        if direction == 'up' and index > 0:
            lst[index], lst[index - 1] = lst[index - 1], lst[index]
            self.item_moved.emit(index, 'list1' if lst is self.list1 else 'list2',
                                 index - 1, 'list1' if lst is self.list1 else 'list2')
        elif direction == 'down' and index < len(lst) - 1:
            lst[index], lst[index + 1] = lst[index + 1], lst[index]
            self.item_moved.emit(index, 'list1' if lst is self.list1 else 'list2',
                                 index + 1, 'list1' if lst is self.list1 else 'list2')
class MainWindow(QMainWindow):
    def __init__(self, list_manager):
        super().__init__()
        self.list_manager = list_manager
        self.list_manager.request_update.connect(self.update_ui)  # Make sure this line is added
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.list_widget1 = QListWidget()
        self.list_widget2 = QListWidget()
        self.setup_list_widget(self.list_widget1, self.list_manager.list1)
        self.setup_list_widget(self.list_widget2, self.list_manager.list2)
        
        delegate = AlternatingColorDelegate()
        self.list_widget1.setItemDelegate(delegate)
        self.list_widget2.setItemDelegate(delegate)

        self.tabs.addTab(self.list_widget1, "List 1")
        self.tabs.addTab(self.list_widget2, "List 2")

        btn_move_to_other_list = QPushButton('Move to Other List')
        btn_move_to_other_list.clicked.connect(self.move_selected)
        btn_move_up = QPushButton('Move Up')
        btn_move_up.clicked.connect(lambda: self.move_up_down('up'))
        btn_move_down = QPushButton('Move Down')
        btn_move_down.clicked.connect(lambda: self.move_up_down('down'))

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(btn_move_to_other_list)
        layout.addWidget(btn_move_up)
        layout.addWidget(btn_move_down)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def setup_list_widget(self, list_widget, data_list):
        list_widget.itemDoubleClicked.connect(self.rename_item)
        for item_data in data_list:
            item = QListWidgetItem(item_data[self.list_manager.display_key])
            list_widget.addItem(item)

    def rename_item(self, item):
        current_widget = self.tabs.currentWidget()
        index = current_widget.row(item)
        old_value = item.text()
        line_edit = QLineEdit(old_value)
        line_edit.selectAll()
        line_edit.editingFinished.connect(lambda: self.finish_editing(line_edit, item, current_widget))
        current_widget.setItemWidget(item, line_edit)
        line_edit.setFocus()

    def finish_editing(self, line_edit, item, list_widget):
        new_value = line_edit.text()
        index = list_widget.row(item)
        list_data = self.list_manager.list1 if list_widget is self.list_widget1 else self.list_manager.list2
        list_data[index][self.list_manager.display_key] = new_value
        item.setText(new_value)
        list_widget.setItemWidget(item, None)
        list_name = 'list1' if list_widget is self.list_widget1 else 'list2'
        self.list_manager.item_renamed.emit(index, list_name, new_value)

    def move_selected(self):
        current_widget = self.tabs.currentWidget()
        target_widget = self.list_widget2 if current_widget is self.list_widget1 else self.list_widget1
        current_row = current_widget.currentRow()
        if current_row != -1:
            self.list_manager.move_item(
                self.list_manager.list1 if current_widget is self.list_widget1 else self.list_manager.list2,
                self.list_manager.list2 if target_widget is self.list_widget2 else self.list_manager.list1,
                current_row
            )
        self.update_ui()

    def move_up_down(self, direction):
        current_widget = self.tabs.currentWidget()
        list_ref = self.list_manager.list1 if current_widget is self.list_widget1 else self.list_manager.list2
        current_row = current_widget.currentRow()
        if current_row != -1:
            self.list_manager.move_up_down(list_ref, current_row, direction)
        self.update_ui()

    def update_ui(self):
        self.list_widget1.clear()
        self.list_widget2.clear()
        for item in self.list_manager.list1:
            self.list_widget1.addItem(item[self.list_manager.display_key])
        for item in self.list_manager.list2:
            self.list_widget2.addItem(item[self.list_manager.display_key])

def external_item_moved_handler(old_index, old_list, new_index, new_list):
    print(f'Item moved from {old_list} at index {old_index} to {new_list} at index {new_index}')

def external_item_renamed_handler(index, list_name, new_value):
    print(f'Item in {list_name} at index {index} renamed to {new_value}')

