"""
Project Model - Data structure cho project information
"""
from typing import Optional
from pydantic import BaseModel, Field


class ProjectData(BaseModel):
    """Model cho project data từ model.json"""
    
    Project_Name: str = Field(..., description="Tên project")
    LM_Script: int = Field(..., description="Laser script number")
    LM_Num: int = Field(..., description="Laser number (panel number)")
    PSN_PRE: str = Field(..., description="PSN prefix")
    
    class Config:
        """Pydantic config"""
        extra = "allow"  # Allow additional fields


class ProjectSettings(BaseModel):
    """Model cho project settings trong settings.json"""
    
    current_project: str = Field(default="", description="Current selected project")
    psn_pre: str = Field(default="", description="PSN prefix của project hiện tại")
    
    class Config:
        """Pydantic config"""
        extra = "allow"

