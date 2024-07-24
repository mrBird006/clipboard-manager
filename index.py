import sys
import time
import threading
from threading import Thread
from datetime import datetime
import keyboard
import pyperclip
import pyautogui
from list import ListManager, MainWindow
from PyQt5.QtWidgets import QApplication

stop_typing = False
typing_thread = None

def get_clipboard_content():
    return pyperclip.paste() 

def handle_copy(manager):
    #Might get fired before clipboard is updated
    time.sleep(0.5)
    data = get_clipboard_content()

    manager.add_item('list1', {'name': f'{data[:100]}...' if len(data)>100 else data, 'payload': data})


def get_to_paste(manager):
    # Triggered by the hotkey
    print("Hotkey activated!")
    # Perform an action with the manager here
    pasted_element = manager.get_item('list1',0)
    manager.transfer_first_element()
    return pasted_element["payload"] if pasted_element else ""


def type_clipboard_content(mode='enter', clipboard_content=""):
    global stop_typing

    if isinstance(clipboard_content, str):
        lines = [line.strip('\r') for line in clipboard_content.split('\n')]
        time.sleep(1)
        for i in range(0, len(lines)):
            line = lines[i]
            if mode == 'delegate_indentation':
                line = line.strip()
            for char in line:
                if stop_typing:
                    break
                pyautogui.write(char, interval=0.0005)
            if stop_typing or i==len(lines)-1:
                break
            # Handle the newline character based on the mode
            pyautogui.press('esc')#to not hit enter on IDE's autocompleting sugestion
            if mode == 'shift_enter':
                pyautogui.hotkey('shift', 'enter')
            else:
                pyautogui.press('enter')

# Function to stop the script
def stop_script():
    print("\nStopped listening for hotkeys.")
    exit()

def type_with_mode(mode, content):
    global stop_typing, typing_thread
    if typing_thread and typing_thread.is_alive():
        print("Typing is already in progress, skipping this request.")
        return
    stop_typing = False
    print(f"Typing new line with {mode} mode")
    typing_thread = threading.Thread(target=type_clipboard_content, args=(mode,content))
    typing_thread.start()

def listen_for_esc():
    global stop_typing
    while True:
        keyboard.wait('esc',suppress=True)
        stop_typing = True
        print("Esc key pressed. Setting stop_typing to True.")

def paste_mode(content):
    pyperclip.copy(content)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'v')
    
def listen_for_hotkeys(manager):
    type_enter_mode_combination = "ctrl+alt+1"
    type_shift_enter_mode_combination = "ctrl+alt+2"
    type_delegate_indentation_combination = "ctrl+alt+3"

    paste_at_once_hotkey_combination = "ctrl+alt+0"
    copy_hotkey_combination= 'ctrl+c'
    cut_hotkey_combination= 'ctrl+x'
    print(f"Press {type_enter_mode_combination} to start typing the clipboard content pressing 'enter' to type a new line...")
    print(f"Press {type_shift_enter_mode_combination} to start typing the clipboard content pressing 'shift+enter' to type a new line...")
    print(f"Press {type_delegate_indentation_combination} to start typing delegating the indentation to the IDE...")
    print(f"Press {paste_at_once_hotkey_combination} to paste queued element")

    keyboard.add_hotkey(type_enter_mode_combination, lambda: type_with_mode(mode="enter",content=get_to_paste(manager)))
    keyboard.add_hotkey(type_shift_enter_mode_combination, lambda: type_with_mode(mode="shift_enter",content=get_to_paste(manager)))
    keyboard.add_hotkey(type_delegate_indentation_combination, lambda: type_with_mode(mode="delegate_indentation",content=get_to_paste(manager)))
    keyboard.add_hotkey(paste_at_once_hotkey_combination, lambda: paste_mode(content=get_to_paste(manager)))
    keyboard.add_hotkey(copy_hotkey_combination, lambda: handle_copy(manager))
    keyboard.add_hotkey(cut_hotkey_combination, lambda: handle_copy(manager))
    print("Listening for hotkeys...")

    esc_listener_thread = threading.Thread(target=listen_for_esc)
    esc_listener_thread.daemon = True
    esc_listener_thread.start()
    
    keyboard.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = ListManager([], [], 'name')
    
    window = MainWindow(manager)
    window.show()

    # Create a thread to listen for hotkeys
    hotkey_thread = Thread(target=listen_for_hotkeys, args=(manager,))
    hotkey_thread.daemon = True  # Optional: Makes the thread exit when the main thread exits
    hotkey_thread.start()

    # Start the PyQt application loop
    sys.exit(app.exec_())