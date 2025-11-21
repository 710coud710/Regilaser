# Hướng Dẫn Sử Dụng Logging

## 📋 Cách Sử Dụng Cơ Bản

### 1. Import logger vào file của bạn

```python
from utils.Logging import getLogger

# Khởi tạo logger (đầu file, sau imports)
log = getLogger()
```

### 2. Sử dụng các log levels

```python
# DEBUG - Chi tiết cho debugging
log.debug("Chi tiết kỹ thuật để debug")

# INFO - Thông tin bình thường
log.info("Chương trình đã khởi động")
log.info("Kết nối SFIS thành công")

# WARNING - Cảnh báo
log.warning("Tài nguyên sắp hết")
log.warning("COM port chưa được chọn")

# ERROR - Lỗi có thể xử lý được
log.error("Không thể mở file cấu hình")
log.error("Gửi dữ liệu thất bại")

# CRITICAL - Lỗi nghiêm trọng
log.critical("Mất kết nối database")
log.critical("Hệ thống sẽ tắt")
```

## 📁 Ví Dụ Sử Dụng Trong Các File

### Ví dụ 1: main.py
```python
"""Main Entry Point"""
import sys
from PySide6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from presenter.main_presenter import MainPresenter
from utils.Logging import getLogger
import signal

log = getLogger()

def main():
    """Khởi động ứng dụng"""
    log.info("=" * 70)
    log.info("Khởi động ứng dụng Regilazi...")
    
    app = QApplication(sys.argv)
    log.info("QApplication initialized")
    
    # Tạo main window
    window = MainWindow()
    log.info("MainWindow created")
    
    # Tạo presenter
    presenter = MainPresenter(window)
    log.info("MainPresenter initialized")
    
    # Khởi tạo hệ thống
    presenter.initialize()
    
    # Hiển thị window
    window.show()
    log.info("Application window shown")
    
    # Cho phép Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Chạy ứng dụng
    log.info("Application running...")
    exit_code = app.exec()
    
    # Cleanup
    log.info("Application closing...")
    presenter.cleanup()
    log.info("Cleanup completed")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```

### Ví dụ 2: presenter/main_presenter.py
```python
"""Main Presenter"""
from PySide6.QtCore import QObject, Signal
from presenter.sfis_presenter import SFISPresenter
from utils.Logging import getLogger

log = getLogger()

class MainPresenter(QObject):
    logMessage = Signal(str, str)
    
    def __init__(self, main_window):
        super().__init__()
        log.info("MainPresenter.__init__ started")
        
        self.main_window = main_window
        self.sfis_presenter = SFISPresenter()
        
        self.connectSignals()
        log.info("MainPresenter initialized successfully")
    
    def onStartClicked(self):
        """Xử lý khi nhấn START"""
        log.info("=" * 70)
        log.info("START button clicked")
        
        if self.isRunning:
            log.warning("System is already running")
            return
        
        if not self.sfis_presenter.isConnected:
            log.error("SFIS not connected")
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            return
        
        # Lấy dữ liệu
        topPanel = self.main_window.getTopPanel()
        mo = topPanel.getMO()
        allPartsSn = topPanel.getAllPartsSN()
        
        log.info(f"MO: {mo}")
        log.info(f"ALL PARTS SN: {allPartsSn}")
        
        # Gửi START signal
        log.info("Sending START signal to SFIS...")
        success = self.sfis_presenter.sendStartSignal(mo, allPartsSn, mo)
        
        if success:
            log.info("START signal request sent successfully")
        else:
            log.error("Failed to send START signal")
```

### Ví dụ 3: presenter/sfis_presenter.py
```python
"""SFIS Presenter"""
from PySide6.QtCore import QObject, Signal
from utils.Logging import getLogger

log = getLogger()

class SFISPresenter(QObject):
    
    def connect(self, portName):
        """Kết nối SFIS"""
        log.info(f"Connecting to SFIS on {portName}...")
        
        success = self.sfis_worker.connect(portName)
        
        if success:
            log.info(f"SFIS connected successfully: {portName}")
            self.currentPort = portName
        else:
            log.error(f"Failed to connect SFIS: {portName}")
        
        return success
    
    def sendStartSignal(self, mo, all_parts_no, panel_no):
        """Gửi START signal"""
        log.info("sendStartSignal() called")
        log.debug(f"Parameters: mo={mo}, parts={all_parts_no}, panel={panel_no}")
        
        if not self.isConnected:
            log.error("Cannot send START signal: Not connected")
            return False
        
        # Tạo message
        start_message = self.sfis_model.createStartSignal(mo, all_parts_no, panel_no)
        
        if not start_message:
            log.error("Failed to create START signal message")
            return False
        
        log.debug(f"START message: {start_message}")
        log.info("Invoking worker to send START signal...")
        
        # Invoke worker
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self.start_worker,
            "send_start_signal",
            Qt.QueuedConnection,
            Q_ARG(str, start_message)
        )
        
        log.info("Worker invoked successfully")
        return True
```

### Ví dụ 4: workers/sfis_worker.py
```python
"""SFIS Worker"""
from PySide6.QtCore import QObject, Signal
import serial
from utils.Logging import getLogger

log = getLogger()

class SFISWorker(QObject):
    
    def connect(self, port_name=None, baudrate=None):
        """Kết nối COM port"""
        log.info(f"SFISWorker.connect() - port={port_name}, baud={baudrate}")
        
        try:
            if port_name:
                self.port_name = port_name
            
            log.debug(f"Opening serial port: {self.port_name}")
            
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            self.is_connected = True
            log.info(f"Serial port opened successfully: {self.port_name}")
            self.connectionStatusChanged.emit(True)
            return True
            
        except Exception as e:
            log.error(f"Failed to open serial port: {str(e)}")
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            return False
    
    def send_data(self, data):
        """Gửi dữ liệu"""
        log.debug(f"send_data() called with {len(data)} bytes")
        
        try:
            if not self.is_connected:
                log.error("Cannot send: Not connected")
                return False
            
            data_bytes = data.encode('ascii')
            log.debug(f"Sending: {data}")
            
            self.serial_port.write(data_bytes)
            self.serial_port.flush()
            
            log.info(f"Data sent successfully: {len(data)} bytes")
            return True
            
        except Exception as e:
            log.error(f"Failed to send data: {str(e)}")
            return False
```

### Ví dụ 5: model/sfis_model.py
```python
"""SFIS Model"""
from PySide6.QtCore import QObject, Signal
from utils.Logging import getLogger

log = getLogger()

class SFISModel(QObject):
    
    def createStartSignal(self, mo, all_parts_no, panel_no):
        """Tạo START signal"""
        log.info("Creating START signal...")
        log.debug(f"Input: MO={mo}, PARTS={all_parts_no}, PANEL={panel_no}")
        
        try:
            # Padding
            mo_padded = mo.ljust(self.MO_LENGTH)[:self.MO_LENGTH]
            all_parts_padded = all_parts_no.ljust(self.ALL_PARTS_NO_LENGTH)[:self.ALL_PARTS_NO_LENGTH]
            panel_padded = panel_no.ljust(self.PANEL_NO_LENGTH)[:self.PANEL_NO_LENGTH]
            
            # Tạo message
            start_signal = f"{mo_padded}{all_parts_padded}{panel_padded}START"
            
            log.info(f"START signal created: {len(start_signal)} bytes")
            log.debug(f"Content: {start_signal}")
            
            return start_signal
            
        except Exception as e:
            log.error(f"Failed to create START signal: {str(e)}")
            return None
```

## 🎨 Format Log Output

### Console (có màu):
```
[2025-11-21 15:30:45] [INFO   ] [main.py] [main:15] [Name=MainThread] Khởi động ứng dụng...
[2025-11-21 15:30:45] [INFO   ] [sfis_presenter.py] [connect:50] [Name=MainThread] Connecting to SFIS on COM2...
[2025-11-21 15:30:45] [DEBUG  ] [sfis_worker.py] [connect:28] [Name=SFISThread] Opening serial port: COM2
```

### File log (không màu):
```
[2025-11-21 15:30:45] [INFO   ] [main.py] [main:15] [Name=MainThread] Khởi động ứng dụng...
[2025-11-21 15:30:45] [INFO   ] [sfis_presenter.py] [connect:50] [Name=MainThread] Connecting to SFIS on COM2...
[2025-11-21 15:30:45] [DEBUG  ] [sfis_worker.py] [connect:28] [Name=SFISThread] Opening serial port: COM2
```

## 📊 Best Practices

### 1. Log Level Guidelines
- **DEBUG**: Chi tiết kỹ thuật, biến số, data flow
- **INFO**: Các sự kiện quan trọng (start, stop, connect, success)
- **WARNING**: Vấn đề nhỏ nhưng chương trình vẫn chạy
- **ERROR**: Lỗi cần chú ý nhưng không crash
- **CRITICAL**: Lỗi nghiêm trọng, có thể crash

### 2. Log Messages
```python
# ✅ GOOD - Rõ ràng, có context
log.info("SFIS connected successfully on COM2")
log.error(f"Failed to send data: {error_msg}")
log.debug(f"Received data: {data[:50]}...")  # Giới hạn độ dài

# ❌ BAD - Quá chung chung
log.info("Success")
log.error("Error")
```

### 3. Exception Logging
```python
try:
    # code
except Exception as e:
    log.error(f"Failed to connect SFIS: {str(e)}")
    log.debug(f"Exception details: {e}", exc_info=True)  # Include traceback
```

### 4. Thêm separator cho dễ đọc
```python
log.info("=" * 70)
log.info("BẮT ĐẦU QUY TRÌNH TEST")
log.info("=" * 70)
```

## 🔧 Configuration

### Thay đổi log level cho console
Trong `utils/Logging.py`:
```python
console_handler.setLevel(logging.INFO)  # INFO, DEBUG, WARNING, ERROR
```

### Thay đổi log level cho file
```python
file_handler.setLevel(logging.DEBUG)  # Thường để DEBUG để log đầy đủ
```

## 📝 Tips

1. **Import logger ở đầu file** ngay sau imports
2. **Sử dụng f-string** để format message với dữ liệu
3. **Log trước và sau** các thao tác quan trọng
4. **Dùng DEBUG** cho chi tiết, INFO cho tổng quan
5. **Log cả success và failure** để dễ trace
6. **Thêm context** vào log message (port name, file name, etc.)

