from dataclasses import dataclass
from typing import Optional, List
from PySide6.QtCore import QObject, Signal
from utils.setting import settings_manager
from utils.Logging import getLogger
log = getLogger()

@dataclass
class LaserData:
    """Cấu trúc dữ liệu laser"""
    mo: str = ""  # Manufacturing Order (20 bytes)
    panel_no: str = ""  # Panel Number (20 bytes)
    psn_list: List[str] = None  # List of PSN (10 items, 20 bytes each)
    # slot_list:list = [0,2,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40]  
    
    def __post_init__(self):
        if self.psn_list is None:
            self.psn_list = []
    
class LaserModel(QObject):
    """Model xử lý logic laser"""
    data_parsed = Signal(object)  # LaserData đã parse
    
    def __init__(self):
        super().__init__()
        self.current_data = LaserData()
        
    def parseResponse(self, response):
        """Parse response từ laser"""
        try:
            self.current_data.mo = response[25:45]
            self.current_data.panel_no = response[45:65]
            self.current_data.psn_list = response[65:].split(',')
        except Exception as e:
            log.error(f"Error parsing response: {str(e)}")
            return None
        return self.current_data

    def createFormatLaser(self, mo=None, panel_no=None, psn_list=None):
        """Tạo format laser"""
        log.info(f"MO: {mo}")
        log.info(f"Panel No: {panel_no}")
        log.info(f"PSN List: {psn_list}")
        start=6
        step=4
        try:
            #Tạo header của format laser
            header = f"0,{panel_no},2,{mo}"
            format_laser = ""
            #Tạo body của format laser số thứ tự và PSN
            for i, slot in enumerate(psn_list):
                index_value = start + i * step
                format_laser += f",{index_value},{slot}"
                # log.info(f"Index: {index_value}, PSN: {slot}")
            
            body = f"{format_laser}"
            content = f"{header}{body}"
            log.info(f"Format laser: {content}")
            return content
        except Exception as e:
            log.error(f"Error creating format laser: {str(e)}")
            return None