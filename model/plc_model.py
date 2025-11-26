"""
PLC Model - Quản lý dữ liệu và logic cơ bản cho PLC
"""
from dataclasses import dataclass
from typing import List
from PySide6.QtCore import QObject, Signal


@dataclass
class PLCCommand:
    """Định nghĩa một lệnh gửi tới PLC"""
    label: str = ""
    payload: str = ""

    def to_string(self) -> str:
        """Trả về chuỗi ASCII hoàn chỉnh (không thêm CRLF)"""
        if self.payload:
            return f"{self.label},{self.payload}"
        return self.label


class PLCModel(QObject):
    """Model xử lý logic cơ bản cho PLC"""

    data_parsed = Signal(str)
    validation_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.available_commands: List[str] = ["L_OK", "L_NG", "CHE_OK", "CHE_NG"]

    def build_command(self, label: str, payload: str = "") -> str:
        """Tạo chuỗi lệnh gửi PLC"""
        try:
            cmd = PLCCommand(label.strip().upper(), payload.strip())
            command_str = cmd.to_string()
            if not command_str:
                raise ValueError("Command is empty")
            return command_str
        except Exception as exc:
            self.validation_error.emit(f"Lỗi tạo PLC command: {exc}")
            return ""

    def parse_response(self, response: str) -> str:
        """Hook để parse response nếu cần (tạm thời trả về nguyên văn)"""
        clean = response.strip()
        if not clean:
            self.validation_error.emit("PLC response is empty")
            return ""
        self.data_parsed.emit(clean)
        return clean

