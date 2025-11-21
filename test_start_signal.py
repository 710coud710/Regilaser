"""
Test script cho START Signal functionality
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PySide6.QtCore import QThread
from model.sfis_model import SFISModel
from workers.sfis_worker import SFISWorker
from workers.start_signal_worker import StartSignalWorker
from presenter.sfis_presenter import SFISPresenter


class TestWindow(QMainWindow):
    """Test window để test START signal"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test START Signal")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # Test buttons
        self.btn_test_model = QPushButton("Test 1: SFISModel - Create START Signal")
        self.btn_test_model.clicked.connect(self.test_model)
        layout.addWidget(self.btn_test_model)
        
        self.btn_test_worker = QPushButton("Test 2: StartSignalWorker - Send Signal (Mock)")
        self.btn_test_worker.clicked.connect(self.test_worker)
        layout.addWidget(self.btn_test_worker)
        
        self.btn_test_presenter = QPushButton("Test 3: SFISPresenter - Full Flow (Mock)")
        self.btn_test_presenter.clicked.connect(self.test_presenter)
        layout.addWidget(self.btn_test_presenter)
        
        self.btn_clear = QPushButton("Clear Log")
        self.btn_clear.clicked.connect(self.log_display.clear)
        layout.addWidget(self.btn_clear)
        
        # Initialize components
        self.sfis_model = None
        self.sfis_presenter = None
        
        self.log("=== Test START Signal System ===")
        self.log("Chọn một test để chạy")
    
    def log(self, message, level="INFO"):
        """Log message to display"""
        colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "ERROR": "red",
            "WARNING": "orange",
            "DEBUG": "blue"
        }
        color = colors.get(level, "black")
        self.log_display.append(f'<span style="color: {color};">[{level}] {message}</span>')
    
    def test_model(self):
        """Test SFISModel.createStartSignal()"""
        self.log("\n=== TEST 1: SFISModel ===", "INFO")
        
        try:
            # Khởi tạo model
            model = SFISModel()
            self.log("✓ SFISModel initialized", "SUCCESS")
            
            # Test data
            mo = "MO12345"
            all_parts_no = "ALL123"
            panel_no = "PANEL001"
            
            self.log(f"Input: MO='{mo}', ALL_PARTS='{all_parts_no}', PANEL='{panel_no}'", "INFO")
            
            # Validate
            valid_mo, msg_mo = model.validateMo(mo)
            valid_parts, msg_parts = model.validateAllPartsNo(all_parts_no)
            valid_panel, msg_panel = model.validatePanelNo(panel_no)
            
            if not valid_mo:
                self.log(f"✗ MO validation failed: {msg_mo}", "ERROR")
                return
            if not valid_parts:
                self.log(f"✗ ALL PARTS validation failed: {msg_parts}", "ERROR")
                return
            if not valid_panel:
                self.log(f"✗ PANEL validation failed: {msg_panel}", "ERROR")
                return
            
            self.log("✓ All validations passed", "SUCCESS")
            
            # Create START signal
            start_signal = model.createStartSignal(mo, all_parts_no, panel_no)
            
            if start_signal:
                self.log(f"✓ START signal created successfully", "SUCCESS")
                self.log(f"Signal length: {len(start_signal)} bytes", "INFO")
                self.log(f"Signal content: '{start_signal}'", "DEBUG")
                
                # Verify format
                expected_length = 20 + 12 + 20 + 5  # 57 bytes
                if len(start_signal) == expected_length:
                    self.log(f"✓ Length correct: {expected_length} bytes", "SUCCESS")
                else:
                    self.log(f"✗ Length incorrect: expected {expected_length}, got {len(start_signal)}", "ERROR")
                
                # Check if ends with START
                if start_signal.endswith("START"):
                    self.log("✓ Signal ends with 'START'", "SUCCESS")
                else:
                    self.log("✗ Signal does not end with 'START'", "ERROR")
            else:
                self.log("✗ Failed to create START signal", "ERROR")
                
        except Exception as e:
            self.log(f"✗ Exception: {str(e)}", "ERROR")
    
    def test_worker(self):
        """Test StartSignalWorker (mock)"""
        self.log("\n=== TEST 2: StartSignalWorker (Mock) ===", "INFO")
        
        try:
            # Create mock SFIS worker
            sfis_worker = SFISWorker()
            self.log("✓ SFISWorker created (not connected)", "SUCCESS")
            
            # Create START signal worker
            start_worker = StartSignalWorker(sfis_worker)
            start_thread = QThread()
            start_worker.moveToThread(start_thread)
            
            # Connect signals
            start_worker.signal_sent.connect(
                lambda success, msg: self.log(
                    f"{'✓' if success else '✗'} Signal sent callback: {msg}",
                    "SUCCESS" if success else "ERROR"
                )
            )
            start_worker.log_message.connect(self.log)
            
            start_thread.start()
            self.log("✓ StartSignalWorker thread started", "SUCCESS")
            
            # Create test message
            model = SFISModel()
            test_message = model.createStartSignal("TEST_MO", "TEST_PARTS", "TEST_PANEL")
            
            self.log(f"Test message: '{test_message}'", "DEBUG")
            self.log("Note: Send will fail because not connected to real COM port", "WARNING")
            
            # Try to send (will fail because not connected)
            from PySide6.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                start_worker,
                "send_start_signal",
                Qt.QueuedConnection,
                Q_ARG(str, test_message)
            )
            
            self.log("✓ Worker invoked (check callback above)", "INFO")
            
            # Cleanup
            QThread.msleep(100)  # Wait for worker to finish
            start_thread.quit()
            start_thread.wait()
            self.log("✓ Thread cleaned up", "SUCCESS")
            
        except Exception as e:
            self.log(f"✗ Exception: {str(e)}", "ERROR")
    
    def test_presenter(self):
        """Test SFISPresenter (mock)"""
        self.log("\n=== TEST 3: SFISPresenter (Mock) ===", "INFO")
        self.log("Note: This test will fail without real COM port connection", "WARNING")
        
        try:
            # Create presenter
            if not self.sfis_presenter:
                self.sfis_presenter = SFISPresenter()
                
                # Connect signals
                self.sfis_presenter.logMessage.connect(self.log)
                self.sfis_presenter.startSignalSent.connect(
                    lambda success, msg: self.log(
                        f"{'✓' if success else '✗'} START signal sent: {msg}",
                        "SUCCESS" if success else "ERROR"
                    )
                )
                
                self.log("✓ SFISPresenter initialized", "SUCCESS")
            
            # Try to send START signal (will fail - not connected)
            mo = "TEST_MO_123"
            all_parts = "TEST_PARTS"
            panel = "TEST_PANEL"
            
            self.log(f"Attempting to send START signal...", "INFO")
            self.log(f"  MO: {mo}", "DEBUG")
            self.log(f"  ALL PARTS: {all_parts}", "DEBUG")
            self.log(f"  PANEL: {panel}", "DEBUG")
            
            success = self.sfis_presenter.sendStartSignal(mo, all_parts, panel)
            
            if not success:
                self.log("Expected: Not connected error", "INFO")
            
        except Exception as e:
            self.log(f"✗ Exception: {str(e)}", "ERROR")
    
    def closeEvent(self, event):
        """Cleanup on close"""
        if self.sfis_presenter:
            self.sfis_presenter.cleanup()
        event.accept()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

