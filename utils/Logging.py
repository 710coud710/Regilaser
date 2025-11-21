"""
Logging Module - Hệ thống logging cho ứng dụng
Hỗ trợ logging ra console (có màu) và file (theo ngày)
"""
import logging
import os
import threading
from datetime import datetime

# Màu ANSI cho console
COLOR = {
    "RESET": "\033[0m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "GRAY": "\033[90m",
}


class ColoredFormatter(logging.Formatter):
    """Formatter có màu cho console output"""
    
    COLORS = {
        logging.DEBUG: COLOR["CYAN"],
        logging.INFO: COLOR["GREEN"],
        logging.WARNING: COLOR["YELLOW"],
        logging.ERROR: COLOR["RED"],
        logging.CRITICAL: COLOR["MAGENTA"],
    }

    def format(self, record):
        # Tạo bản sao record để không ảnh hưởng đến các handler khác
        record_copy = logging.makeLogRecord(record.__dict__)
        
        # Màu cho level (căn lề trái, độ rộng cố định)
        color_level = self.COLORS.get(record_copy.levelno, COLOR["WHITE"])
        record_copy.levelname = f"{color_level}{record_copy.levelname:<7}{COLOR['RESET']}"
        
        # Màu xám nhạt cho metadata
        record_copy.filename = f"{COLOR['GRAY']}{record_copy.filename}{COLOR['RESET']}"
        record_copy.funcName = f"{COLOR['GRAY']}{record_copy.funcName}{COLOR['RESET']}"
        record_copy.threadName = f"{COLOR['GRAY']}{record_copy.threadName}{COLOR['RESET']}"
        
        # Message giữ nguyên màu trắng
        if not isinstance(record_copy.msg, str):
            record_copy.msg = str(record_copy.msg)
        
        return super().format(record_copy)


class ThreadLogger:
    """
    Thread-safe Singleton Logger
    Tự động tạo log file theo ngày trong thư mục logs/
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, log_name="Regilazi", log_dir="logs"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)

                # Tạo thư mục logs nếu chưa có
                os.makedirs(log_dir, exist_ok=True)

                logger = logging.getLogger(log_name)
                logger.setLevel(logging.DEBUG)
                logger.propagate = False

                if not logger.handlers:

                    # ===== FORMAT GIỐNG NHAU CHO CONSOLE VÀ FILE =====
                    log_format = (
                        "[%(asctime)s] "
                        "[%(levelname)s] "
                        "[%(filename)s] "
                        "[%(funcName)s:%(lineno)d] "
                        "[Name=%(threadName)s] "
                        "%(message)s"
                    )

                    # ===== Console handler có màu =====
                    console_handler = logging.StreamHandler()
                    console_handler.setFormatter(
                        ColoredFormatter(log_format, "%Y-%m-%d %H:%M:%S")
                    )
                    console_handler.setLevel(logging.INFO)

                    # ===== File =====
                    # File name: Regilazi_2025-11-21.log
                    today = datetime.now().strftime("%Y-%m-%d")
                    log_filename = os.path.join(log_dir, f"{log_name}_{today}.log")
                    
                    file_handler = logging.FileHandler(
                        filename=log_filename,
                        mode='a',  # Append mode
                        encoding="utf-8"
                    )
                    
                    file_handler.setFormatter(
                        logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")
                    )
                    file_handler.setLevel(logging.DEBUG)

                    # Thêm handlers vào logger
                    logger.addHandler(console_handler)
                    logger.addHandler(file_handler)
                    
                    # Log khởi động
                    logger.info(f"Logger initialized: {log_name}")
                    logger.info(f"Log file: {log_filename}")
                    logger.info("=" * 10)

                cls._instance.logger = logger

            return cls._instance

    def __getattr__(self, name):
        """Proxy method để gọi trực tiếp các method của logger"""
        return getattr(self.logger, name)


#Hàm tiện ích để lấy logger
def getLogger(name="Regilazi"):
    return ThreadLogger(log_name=name).logger


if __name__ == "__main__":     
    log = getLogger()
    
    log.debug("Debug message - Chi tiết cho debugging")
    log.info("Info message - Thông tin hoạt động bình thường")
    log.warning("Warning message - Cảnh báo: Tài nguyên sắp cạn")
    log.error("Error message - Lỗi khi mở file cấu hình")
    log.critical("Critical message - Lỗi nghiêm trọng, chương trình sẽ tự hủy")

