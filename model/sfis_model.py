"""
SFIS Model - Logic nghiệp vụ và cấu trúc dữ liệu cho SFIS
"""
from dataclasses import dataclass
from typing import Optional, List
from PySide6.QtCore import QObject, Signal
from config import ConfigManager


@dataclass
class SFISData:
    """Cấu trúc dữ liệu SFIS"""
    # Request data
    mo: str = ""  # Manufacturing Order (20 bytes)
    all_parts_no: str = ""  # ALL PARTS NO (12 bytes)
    panel_no: str = ""  # Panel Number (20 bytes)
    
    # Response data
    laser_sn: str = ""  # Laser Serial Number (25 bytes)
    security_code: str = ""  # Security Code (25 bytes)
    status: str = ""  # Status (20 bytes)
    
    # PSN data (if using old format)
    psn_list: List[str] = None  # List of PSN (10 items, 20 bytes each)
    
    def __post_init__(self):
        if self.psn_list is None:
            self.psn_list = []


class SFISModel(QObject):
    """Model xử lý logic SFIS"""
    
    # Signals
    data_parsed = Signal(object)  # SFISData đã parse
    validation_error = Signal(str)  # Lỗi validation
    
    # Constants - Định dạng mới
    LASER_SN_LENGTH = 25
    SECURITY_CODE_LENGTH = 25
    STATUS_LENGTH = 20
    PASS_KEYWORD = "PASS"
    NEW_FORMAT_LENGTH = 70  # 25 + 25 + 20 (không tính PASS vì nó nằm trong status)
    
    # Constants - Định dạng cũ
    MO_LENGTH = 20
    PANEL_NO_LENGTH = 20
    ALL_PARTS_NO_LENGTH = 12
    PSN_LENGTH = 20
    PSN_COUNT = 10
    NEED_KEYWORD = "NEED"
    PSN10_KEYWORD = "PSN10"
    END_KEYWORD = "END"
    
    def __init__(self):
        super().__init__()
        self.current_data = SFISData()
        # Khởi tạo ConfigManager (singleton)
        self.config_manager = ConfigManager()
    
    def createRequestPsn(self, mo, all_parts_no, panel_no):
        """ MO(20) + AllPar_NO(12) + PANEL_NO(20) + NEEDPSN10(9)
        Total: 61 bytes    
        """
        try:
            # Padding các field đúng độ dài
            mo_padded = mo.ljust(self.MO_LENGTH)[:self.MO_LENGTH]
            all_parts_padded = all_parts_no.ljust(self.ALL_PARTS_NO_LENGTH)[:self.ALL_PARTS_NO_LENGTH]
            panel_padded = panel_no.ljust(self.PANEL_NO_LENGTH)[:self.PANEL_NO_LENGTH]
            
            # Tạo request string
            request = f"{mo_padded}{all_parts_padded}{panel_padded}{self.NEED_KEYWORD}{self.PSN10_KEYWORD}"
            
            # Lưu vào current_data
            self.current_data.mo = mo
            self.current_data.all_parts_no = all_parts_no
            self.current_data.panel_no = panel_no
            
            return request
            
        except Exception as e:
            self.validation_error.emit(f"Lỗi tạo request: {str(e)}")
            return None
    
    def parseResponsePsn(self, response):

        try:
            expected_length = self.MO_LENGTH + self.PANEL_NO_LENGTH + (self.PSN_LENGTH * self.PSN_COUNT) + 4
            
            if len(response) < expected_length:
                self.validation_error.emit(f"Response quá ngắn: {len(response)} < {expected_length}")
                return None
            
            # Parse các field
            pos = 0
            mo = response[pos:pos + self.MO_LENGTH].strip()
            pos += self.MO_LENGTH
            
            panel_no = response[pos:pos + self.PANEL_NO_LENGTH].strip()
            pos += self.PANEL_NO_LENGTH
            
            # Parse 10 PSN
            psn_list = []
            for i in range(self.PSN_COUNT):
                psn = response[pos:pos + self.PSN_LENGTH].strip()
                psn_list.append(psn)
                pos += self.PSN_LENGTH
            
            # Kiểm tra PASS
            pass_keyword = response[pos:pos + 4]
            if pass_keyword != self.PASS_KEYWORD:
                self.validation_error.emit(f"Không tìm thấy PASS keyword: {pass_keyword}")
                return None
            
            # Cập nhật current_data
            self.current_data.mo = mo
            self.current_data.panel_no = panel_no
            self.current_data.psn_list = psn_list
            
            self.data_parsed.emit(self.current_data)
            return self.current_data
            
        except Exception as e:
            self.validation_error.emit(f"Lỗi parse response: {str(e)}")
            return None
    
    def parseResponseNewFormat(self, response):
        """
        Parse phản hồi SFIS định dạng mới
        
        Format: LaserSN(25) + SecurityCode(25) + Status(20) + PASS(4)
        Total: 74 bytes
        
        Example: "GR93J80034260001         52-005353                00S0PASS"
        
        Args:
            response (str): Response string từ SFIS
            
        Returns:
            SFISData: Dữ liệu đã parse, hoặc None nếu lỗi
        """
        try:
            # Kiểm tra độ dài và PASS keyword
            if len(response) < self.NEW_FORMAT_LENGTH:
                self.validation_error.emit(f"Response quá ngắn: {len(response)} < {self.NEW_FORMAT_LENGTH}")
                return None
            
            if self.PASS_KEYWORD not in response:
                self.validation_error.emit(f"Không tìm thấy PASS keyword trong response")
                return None
            
            # Parse các field
            pos = 0
            laser_sn = response[pos:pos + self.LASER_SN_LENGTH].strip()
            pos += self.LASER_SN_LENGTH
            
            security_code = response[pos:pos + self.SECURITY_CODE_LENGTH].strip()
            pos += self.SECURITY_CODE_LENGTH
            
            status = response[pos:pos + self.STATUS_LENGTH].strip()
            
            # Cập nhật current_data
            self.current_data.laser_sn = laser_sn
            self.current_data.security_code = security_code
            self.current_data.status = status
            
            self.data_parsed.emit(self.current_data)
            return self.current_data
            
        except Exception as e:
            self.validation_error.emit(f"Lỗi parse response: {str(e)}")
            return None
    
    def createStartSignal(self, mo=None, all_parts_no=None, panel_no=None):
        """ 
        Format: MO(20) + Panel_Number(20) + NEEDPSNxx(9) = 49 bytes
        - MO: Lấy từ config.yaml nếu không truyền vào
        - Panel_Number: Để trống (20 spaces)
        - NEEDPSNxx: Động theo Panel_Num từ config (ex: Panel_Num=5 → NEEDPSN05)       
        """
        try:
            # Lấy config từ ConfigManager
            config = self.config_manager.get()
            
            if not config:
                self.validation_error.emit("Không thể đọc config")
                return None
            
            # Nếu không truyền MO, lấy từ config
            if not mo:
                mo = str(config.MO)
            
            # Lấy Panel_Num từ config để tạo NEEDPSNxx
            panel_num = config.Panel_Num
            
            # Tạo NEEDPSNxx: "NEEDPSN" + 2 số cuối của Panel_Num
            need_keyword = f"NEEDPSN{panel_num:02d}"  # Format 2 chữ số, thêm 0 phía trước nếu cần
            
            # Kiểm tra độ dài keyword (phải là 9 bytes)
            if len(need_keyword) != 9:
                self.validation_error.emit(f"NEEDPSN keyword is not the correct length: {len(need_keyword)} (expected: 9)")
                return None
            
            # MO: 20 bytes
            mo_padded = str(mo).ljust(20)[:20]
            
            # Panel Number: 20 bytes (để trống)
            panel_padded = "".ljust(20)
            
            # Tạo START signal: 20 + 20 + 9 = 49 bytes
            start_signal = f"{mo_padded}{panel_padded}{need_keyword}"
            
            # Lưu vào current_data
            self.current_data.mo = mo
            self.current_data.panel_no = ""
            
            return start_signal
            
        except AttributeError as e:
            error_msg = f"Lỗi đọc config: {str(e)} - Kiểm tra Panel_Num trong config.yaml"
            self.validation_error.emit(error_msg)
            return None
        except Exception as e:
            self.validation_error.emit(f"Lỗi tạo START signal: {str(e)}")
            return None
    
    def createTestComplete(self, mo, panel_no):
        """
        Tạo message báo hoàn thành test
        
        Format: MO(20) + PANEL_NO(20) + END(3)
        Total: 43 bytes
        
        Args:
            mo (str): Manufacturing Order
            panel_no (str): Panel Number
            
        Returns:
            str: Message string (43 bytes)
        """
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
        
        Format: MO(20) + PANEL_NO(20) + END(3) + ErrorCode(6)
        Total: 49 bytes
        
        Args:
            mo (str): Manufacturing Order
            panel_no (str): Panel Number
            error_code (str): Error code (6 chars)
            
        Returns:
            str: Message string (49 bytes)
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

