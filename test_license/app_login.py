import ctypes
import time
from ctypes import wintypes


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

WM_SETTEXT = 0x000C
BM_CLICK = 0x00F5
CB_SELECTSTRING = 0x014D
CB_FINDSTRINGEXACT = 0x0158
CB_SETCURSEL = 0x014E
CB_SHOWDROPDOWN = 0x014F
SW_RESTORE = 9
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

user32.SendMessageW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.SendMessageW.restype = wintypes.LPARAM
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL
user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL
user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE
user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL
kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HANDLE
kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
kernel32.GlobalUnlock.restype = wintypes.BOOL

FIELD_ROW_TOLERANCE = 14


def login_to_app(process_id, config, timeout=30):
    login_window = wait_for_login_window(process_id, timeout)

    try:
        print("Selecting database...")
        select_database(login_window, config["database"])
        print("Database selection step finished")
    except Exception as e:
        print(f"Could not select database automatically: {e}")

    login_window = wait_for_login_window(process_id, 5)
    print("Filling login name...")
    set_text_field_by_label(login_window, "Login name:", config["login_name"])
    print("Filling password...")
    set_text_field_by_label(login_window, "Password:", config["sql_password"])
    print("Submitting login...")
    press_key(0x0D)  # ENTER
    print("Login submitted")


def close_login_popup_if_present(process_id, timeout=10):
    popup = wait_for_popup_window(process_id, timeout)
    if not popup:
        return False

    print(f"Login popup: {get_popup_text(popup)}")
    click_button(popup, "OK")
    return True


def wait_for_popup_window(process_id, timeout=10):
    end_time = time.time() + timeout

    while time.time() < end_time:
        popup = find_popup_window(process_id)
        if popup:
            user32.ShowWindow(popup, SW_RESTORE)
            user32.SetForegroundWindow(popup)
            return popup

        time.sleep(0.5)

    return None


def find_popup_window(process_id):
    matches = []

    def callback(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True

        window_process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_process_id))

        if window_process_id.value != process_id:
            return True

        title = get_window_text(hwnd)
        if "login" in title.lower():
            return True

        if find_child_by_text(hwnd, "OK") and get_popup_text(hwnd):
            matches.append(hwnd)
            return False

        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return matches[0] if matches else None


def get_popup_text(parent_hwnd):
    text_parts = []

    for child in get_child_windows(parent_hwnd):
        text = normalize_control_text(get_window_text(child)).strip()
        if text and text not in {"OK", "Cancel", "Windows Security", "Advanced"}:
            text_parts.append(text)

    return " ".join(text_parts)


def select_database(parent_hwnd, database_name):
    label = find_child_by_text(parent_hwnd, "Database:")
    if not label:
        raise RuntimeError("Could not find label 'Database:'")

    field = find_field_on_label_row(parent_hwnd, label)
    if field:
        select_combo_value(field, database_name)
        if get_window_text(field):
            return

    click_database_dropdown(parent_hwnd, label)
    select_first_dropdown_item(label)


def find_field_on_label_row(parent_hwnd, label):
    label_rect = get_window_rect(label)
    parent_rect = get_window_rect(parent_hwnd)
    candidates = []

    for child in get_child_windows(parent_hwnd):
        rect = get_window_rect(child)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        same_row_distance = abs(vertical_center(rect) - vertical_center(label_rect))
        right_of_label = rect[0] >= label_rect[2]
        in_input_area = rect[2] < parent_rect[0] + ((parent_rect[2] - parent_rect[0]) * 0.75)

        if same_row_distance <= FIELD_ROW_TOLERANCE and right_of_label and in_input_area:
            if width >= 100 and 14 <= height <= 35 and not get_window_text(child):
                candidates.append((same_row_distance, rect[0], child))

    if not candidates:
        return None

    _, _, field = sorted(candidates, key=lambda item: (item[0], item[1]))[0]
    return field


def click_database_dropdown(parent_hwnd, label):
    label_rect = get_window_rect(label)
    parent_rect = get_window_rect(parent_hwnd)

    x = parent_rect[0] + int((parent_rect[2] - parent_rect[0]) * 0.64)
    y = vertical_center(label_rect)
    click_at(x, y)


def select_first_dropdown_item(label):
    time.sleep(0.2)
    left, top, right, bottom = get_window_rect(label)
    click_at(right + 90, bottom + 12)
    time.sleep(0.2)


def wait_for_login_window(process_id, timeout=30):
    end_time = time.time() + timeout

    while time.time() < end_time:
        window = find_login_window(process_id)
        if window:
            user32.ShowWindow(window, SW_RESTORE)
            user32.SetForegroundWindow(window)
            return window

        time.sleep(0.5)

    raise TimeoutError("Login window was not found")


def find_login_window(process_id):
    matches = []

    def callback(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True

        window_process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_process_id))

        if window_process_id.value == process_id and "login" in get_window_text(hwnd).lower():
            matches.append(hwnd)
            return False

        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return matches[0] if matches else None


def set_field_by_label(parent_hwnd, label_text, value, select_from_list=False):
    label = find_child_by_text(parent_hwnd, label_text)
    if not label:
        raise RuntimeError(f"Could not find label '{label_text}'")

    label_rect = get_window_rect(label)
    parent_rect = get_window_rect(parent_hwnd)
    candidates = []

    for child in get_child_windows(parent_hwnd):
        if not is_possible_input_field(child):
            continue

        rect = get_window_rect(child)
        same_row_distance = abs(vertical_center(rect) - vertical_center(label_rect))
        right_of_label = rect[0] > label_rect[2]
        in_input_area = rect[0] < parent_rect[0] + ((parent_rect[2] - parent_rect[0]) * 0.70)

        if same_row_distance <= FIELD_ROW_TOLERANCE and right_of_label and in_input_area:
            candidates.append((same_row_distance, rect[0], child))

    if not candidates:
        raise RuntimeError(
            f"Could not find input field for '{label_text}'. "
            f"Available controls: {describe_child_windows(parent_hwnd)}"
        )

    _, _, field = sorted(candidates, key=lambda item: (item[0], item[1]))[0]

    if select_from_list:
        select_combo_value(field, value)
    else:
        send_text(field, value)


def set_text_field_by_label(parent_hwnd, label_text, value):
    label = find_child_by_text(parent_hwnd, label_text)
    if not label:
        raise RuntimeError(f"Could not find label '{label_text}'")

    label_rect = get_window_rect(label)
    candidates = []

    for child in get_child_windows(parent_hwnd):
        if not user32.IsWindowVisible(child):
            continue

        if "edit" not in get_class_name(child).lower():
            continue

        rect = get_window_rect(child)
        same_row_distance = abs(vertical_center(rect) - vertical_center(label_rect))
        right_of_label = rect[0] > label_rect[2]

        if same_row_distance <= FIELD_ROW_TOLERANCE and right_of_label:
            candidates.append((same_row_distance, rect[0], child))

    if not candidates:
        raise RuntimeError(
            f"Could not find text field for '{label_text}'. "
            f"Available controls: {describe_child_windows(parent_hwnd)}"
        )

    _, _, field = sorted(candidates, key=lambda item: (item[0], item[1]))[0]
    send_text(field, value)

    if label_text != "Password:" and get_window_text(field) != str(value):
        print(f"{label_text} field did not report the expected value after setting")


def click_button(parent_hwnd, button_text):
    button = find_child_by_text(parent_hwnd, button_text)
    if not button:
        raise RuntimeError(f"Could not find button '{button_text}'")

    user32.SendMessageW(button, BM_CLICK, 0, 0)


def find_child_by_text(parent_hwnd, text):
    for child in get_child_windows(parent_hwnd):
        if normalize_control_text(get_window_text(child)) == normalize_control_text(text):
            return child

    return None


def get_child_windows(parent_hwnd):
    children = []

    def callback(hwnd, lparam):
        children.append(hwnd)
        return True

    user32.EnumChildWindows(parent_hwnd, EnumChildProc(callback), 0)
    return children


def is_possible_input_field(hwnd):
    class_name = get_class_name(hwnd).lower()
    text = get_window_text(hwnd)
    left, top, right, bottom = get_window_rect(hwnd)
    width = right - left
    height = bottom - top

    if "button" in class_name or "static" in class_name:
        return False

    if text in {"OK", "Cancel", "Windows Security", "Advanced"}:
        return False

    if text:
        return False

    if "edit" in class_name or "combobox" in class_name:
        return True

    return width >= 100 and 14 <= height <= 35


def send_text(hwnd, text):
    class_name = get_class_name(hwnd).lower()

    if "combobox" in class_name:
        send_combo_box_text(hwnd, text)
        return

    value = str(text)
    paste_text(hwnd, value)

    if get_window_text(hwnd) == value:
        return

    user32.SetFocus(hwnd)
    text_buffer = ctypes.create_unicode_buffer(value)
    user32.SetWindowTextW(hwnd, value)
    user32.SendMessageW(hwnd, WM_SETTEXT, 0, ctypes.addressof(text_buffer))


def send_combo_box_text(hwnd, text):
    value = str(text)
    text_buffer = ctypes.create_unicode_buffer(value)

    select_result = user32.SendMessageW(
        hwnd,
        CB_SELECTSTRING,
        -1,
        ctypes.addressof(text_buffer),
    )

    if select_result != -1:
        return

    edit_child = find_edit_child(hwnd)
    if edit_child:
        send_text(edit_child, value)
        return

    text_buffer = ctypes.create_unicode_buffer(value)
    user32.SetWindowTextW(hwnd, value)
    user32.SendMessageW(hwnd, WM_SETTEXT, 0, ctypes.addressof(text_buffer))


def select_combo_value(hwnd, text):
    value = str(text)
    text_buffer = ctypes.create_unicode_buffer(value)

    exact_index = user32.SendMessageW(
        hwnd,
        CB_FINDSTRINGEXACT,
        -1,
        ctypes.addressof(text_buffer),
    )

    if exact_index != -1:
        user32.SendMessageW(hwnd, CB_SETCURSEL, exact_index, 0)
        return

    select_result = user32.SendMessageW(
        hwnd,
        CB_SELECTSTRING,
        -1,
        ctypes.addressof(text_buffer),
    )

    if select_result != -1:
        return

    select_first_combo_item(hwnd)


def select_first_combo_item(hwnd):
    user32.SetFocus(hwnd)
    click_window_right_side(hwnd)
    user32.SendMessageW(hwnd, CB_SHOWDROPDOWN, True, 0)
    time.sleep(0.2)

    left, top, right, bottom = get_window_rect(hwnd)
    click_at(left + 90, bottom + 12)
    time.sleep(0.2)


def click_window_right_side(hwnd):
    left, top, right, bottom = get_window_rect(hwnd)
    x = right - 10
    y = (top + bottom) // 2

    click_at(x, y)


def click_at(x, y):
    user32.SetCursorPos(x, y)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.05)


def paste_text(hwnd, text):
    user32.SetFocus(hwnd)
    click_window_center(hwnd)
    time.sleep(0.1)
    set_clipboard_text(str(text))
    press_key_combo(0x11, 0x41)  # CTRL + A
    press_key_combo(0x11, 0x56)  # CTRL + V
    time.sleep(0.1)


def click_window_center(hwnd):
    left, top, right, bottom = get_window_rect(hwnd)
    click_at((left + right) // 2, (top + bottom) // 2)


def set_clipboard_text(text):
    data = text + "\0"
    bytes_count = len(data.encode("utf-16-le"))

    if not user32.OpenClipboard(None):
        raise RuntimeError("Could not open clipboard")

    try:
        user32.EmptyClipboard()
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, bytes_count)
        if not handle:
            raise RuntimeError("Could not allocate clipboard memory")

        locked_memory = kernel32.GlobalLock(handle)
        if not locked_memory:
            raise RuntimeError("Could not lock clipboard memory")

        try:
            ctypes.memmove(locked_memory, data.encode("utf-16-le"), bytes_count)
        finally:
            kernel32.GlobalUnlock(handle)

        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise RuntimeError("Could not set clipboard data")
    finally:
        user32.CloseClipboard()


def press_key(virtual_key):
    user32.keybd_event(virtual_key, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(virtual_key, 0, 0x0002, 0)
    time.sleep(0.05)


def press_key_combo(modifier_key, key):
    user32.keybd_event(modifier_key, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(key, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(key, 0, 0x0002, 0)
    time.sleep(0.05)
    user32.keybd_event(modifier_key, 0, 0x0002, 0)
    time.sleep(0.05)


def find_edit_child(parent_hwnd):
    for child in get_child_windows(parent_hwnd):
        if "edit" in get_class_name(child).lower():
            return child

    return None


def describe_child_windows(parent_hwnd):
    descriptions = []

    for child in get_child_windows(parent_hwnd):
        class_name = get_class_name(child)
        text = get_window_text(child)
        rect = get_window_rect(child)
        descriptions.append(f"{class_name!r} text={text!r} rect={rect}")

    return "; ".join(descriptions)


def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def get_class_name(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def get_window_rect(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def vertical_center(rect):
    return (rect[1] + rect[3]) // 2


def normalize_control_text(text):
    return text.replace("&", "")
