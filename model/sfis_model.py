"""
SFIS Model - Logic nghiệp vụ và cấu trúc dữ liệu cho SFIS
"""
from dataclasses import dataclass
from typing import Optional, List
from PySide6.QtCore import QObject, Signal
from config import ConfigManager
from utils.Logging import getLogger
log = getLogger()

@dataclass
class SFISData:
    """Cấu trúc dữ liệu SFIS"""
    # Request data
    mo: str = ""  # Manufacturing Order (20 bytes)
    all_parts_no: str = ""  # ALL PARTS NO (12 bytes)
    panel_no: str = ""  # Panel Number (20 bytes)
    
    # Response data
    laser_sn: str = ""  # Laser Serial Number (25 bytes)
    status: str = ""  # Status (20 bytes)
    
    # PSN data (if using old format)
    psn_list: List[str] = None  # List of PSN (10 items, 20 bytes each)
    keyword: str = ""  # Keyword (4 bytes)
    def __post_init__(self):
        if self.psn_list is None:
            self.psn_list = []


class SFISModel(QObject):
    """Model xử lý logic SFIS"""
    
    # Signals
    data_parsed = Signal(object)  # SFISData đã parse
    validation_error = Signal(str)  # Lỗi validation
    
    # Constants - Định dạng mới
    STATUS_LENGTH = 20
    PASS_KEYWORD = "PASS"   
    # Constants - Định dạng cũ
    MO_LENGTH = 20
    PANEL_NO_LENGTH = 20
    ALL_PARTS_NO_LENGTH = 12
    PSN_LENGTH = 20
    PSN_COUNT = ConfigManager().get().PANEL_NUM
    NEED_KEYWORD = "NEED"

    END_KEYWORD = "END"
    
    def __init__(self):
        super().__init__()
        self.current_data = SFISData()
        # Khởi tạo ConfigManager (singleton)
        self.config_manager = ConfigManager()
        # Lưu số lượng PSN đã request (để parse response)
        self.expected_psn_count = 0

    def parseResponsePsn(self, response):
        """Parse response PSN from SFIS (dynamic based on expected PSN count)"""
        try:
            expected_length = self.MO_LENGTH + self.PANEL_NO_LENGTH + (self.PSN_LENGTH * self.PSN_COUNT) + 4
            
            if len(response) < expected_length:
                self.validation_error.emit(f"Response quá ngắn: {len(response)} < {expected_length}")
                return None
            
            # Parse các field
            pos = 0
            mo = response[pos:pos + self.MO_LENGTH].strip()
            pos += self.MO_LENGTH
            log.info(f"MO: {mo}")
            panel_no = response[pos:pos + self.PANEL_NO_LENGTH].strip()
            pos += self.PANEL_NO_LENGTH
            log.info(f"Panel No: {panel_no}")
            # Parse 10 PSN
            psn_list = []
            for i in range(self.PSN_COUNT):
                psn = response[pos:pos + self.PSN_LENGTH].strip()
                psn_list.append(psn)
                pos += self.PSN_LENGTH
                log.info(f"PSN{i}: {psn}")
            # Kiểm tra PASS
            pass_keyword = response[pos:pos + 4]
            if pass_keyword != self.PASS_KEYWORD:
                self.validation_error.emit(f"Không tìm thấy PASS keyword: {pass_keyword}")
                return None
            log.info(f"PASS Keyword: {pass_keyword}")
            # Cập nhật current_data
            self.current_data.mo = mo
            self.current_data.panel_no = panel_no
            self.current_data.psn_list = psn_list
            self.current_data.keyword = pass_keyword

            self.data_parsed.emit(self.current_data)
            return self.current_data
            
        except Exception as e:
            self.validation_error.emit(f"Lỗi parse response: {str(e)}")
            return None
    
    
    def createFormatNeedPSN(self, mo=None, panel_num=None):
        try:
            # Lấy config từ ConfigManager
            need_keyword = f"NEEDPSN{panel_num}"  # Format theo số panel_num

            # Kiểm tra độ dài keyword (phải là 9 bytes)
            # if len(need_keyword) != 9:
            #     self.validation_error.emit(f"NEEDPSN keyword is not the correct length: {len(need_keyword)} (expected: 9)")
            #     return None
            
            mo_padded = str(mo).ljust(20)[:20] #MO: 20 bytes
            panel_padded = "".ljust(20) # Panel Number: 20 bytes (để trống)
            
            # Tạo START signal: 20 + 20 + 9 = 49 bytes
            start_signal = f"{mo_padded}{panel_padded}{need_keyword}\r\n"
            log.info(f"START signal: {start_signal}")
            # Lưu vào current_data
            self.current_data.mo = mo
            self.current_data.panel_no = ""
            
            return start_signal
            
        except AttributeError as e:
            error_msg = f"Read config error: {str(e)} - Check PANEL_NUM in config.yaml"
            self.validation_error.emit(error_msg)
            return None
        except Exception as e:
            self.validation_error.emit(f"Create START signal error: {str(e)}")
            return None
    
    def createTestComplete(self, mo, panel_no):
        """Tạo message báo hoàn thành test"""
        try:
            mo_padded = mo.ljust(self.MO_LENGTH)[:self.MO_LENGTH]
            panel_padded = panel_no.ljust(self.PANEL_NO_LENGTH)[:self.PANEL_NO_LENGTH]
            
            return f"{mo_padded}{panel_padded}{self.END_KEYWORD}"
            
        except Exception as e:
            self.validation_error.emit(f"Lỗi tạo test complete: {str(e)}")
            return None
    
    def createTestError(self, mo, panel_no, error_code):
        """
        Tạo message báo lỗi test


        """
        try:
            mo_padded = mo.ljust(self.MO_LENGTH)[:self.MO_LENGTH]
            panel_padded = panel_no.ljust(self.PANEL_NO_LENGTH)[:self.PANEL_NO_LENGTH]
            error_padded = error_code.ljust(6)[:6]
            
            return f"{mo_padded}{panel_padded}{self.END_KEYWORD}{error_padded}"
            
        except Exception as e:
            self.validation_error.emit(f"Lỗi tạo test error: {str(e)}")
            return None
    
    def validateMo(self, mo):
        """Validate Manufacturing Order"""
        if not mo or len(mo) == 0:
            return False, "MO không được để trống"
        if len(mo) > self.MO_LENGTH:
            return False, f"MO quá dài (max {self.MO_LENGTH} ký tự)"
        return True, ""
    
    def validatePanelNo(self, panel_no):
        """Validate Panel Number"""
        if not panel_no or len(panel_no) == 0:
            return False, "Panel NO không được để trống"
        if len(panel_no) > self.PANEL_NO_LENGTH:
            return False, f"Panel NO quá dài (max {self.PANEL_NO_LENGTH} ký tự)"
        return True, ""
    
    def validateAllPartsNo(self, all_parts_no):
        """Validate ALL PARTS Number"""
        if not all_parts_no or len(all_parts_no) == 0:
            return False, "ALL PARTS NO không được để trống"
        if len(all_parts_no) > self.ALL_PARTS_NO_LENGTH:
            return False, f"ALL PARTS NO quá dài (max {self.ALL_PARTS_NO_LENGTH} ký tự)"
        return True, ""
    
    def getCurrentData(self):
        """Lấy dữ liệu hiện tại"""
        return self.current_data
    
    def resetData(self):
        """Reset dữ liệu về mặc định"""
        self.current_data = SFISData()

