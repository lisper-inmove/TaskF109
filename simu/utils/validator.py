# utils/validator.py
import re
import socket
from typing import Tuple, Optional

def validate_port(port: int) -> Tuple[bool, str]:
    """验证端口号是否有效"""
    if not isinstance(port, int):
        return False, "端口号必须是整数"
    
    if port < 1 or port > 65535:
        return False, "端口号必须在 1-65535 范围内"
    
    if port < 1024:
        return True, "警告: 使用系统端口 (<1024) 可能需要管理员权限"
    
    return True, "端口号有效"

def validate_ip_address(ip: str) -> Tuple[bool, str]:
    """验证IP地址是否有效"""
    if ip == "0.0.0.0":
        return True, "监听所有地址"
    
    try:
        socket.inet_aton(ip)
        return True, "IP地址有效"
    except socket.error:
        return False, "无效的IP地址"

def validate_config_file(config_file: str) -> Tuple[bool, str]:
    """验证配置文件是否存在且可读"""
    import os
    
    if not os.path.exists(config_file):
        return False, f"配置文件不存在: {config_file}"
    
    if not os.path.isfile(config_file):
        return False, f"配置路径不是文件: {config_file}"
    
    if not os.access(config_file, os.R_OK):
        return False, f"配置文件不可读: {config_file}"
    
    return True, "配置文件有效"