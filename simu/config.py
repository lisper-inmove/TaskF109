# config.py
import json
import os
from typing import Dict, List, Any

class Config:
    """配置管理器"""
    DEFAULT_CONFIG = {
        "server": {
            "host": "0.0.0.0",
            "default_port": 8888,
            "max_connections": 100,
            "receive_buffer_size": 4096,
            "timeout": 30
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "tcp_server.log"
        },
        "protocol": {
            "header_size": 4,
            "max_packet_size": 65536,
            "encoding": "utf-8"
        }
    }
    
    def __init__(self, config_file: str = None):
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str):
        """从文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self._deep_update(self.config, loaded_config)
            print(f"✓ 配置已从 {config_file} 加载")
        except Exception as e:
            print(f"✗ 加载配置文件失败: {e}")
    
    def save_config(self, config_file: str):
        """保存配置到文件"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✓ 配置已保存到 {config_file}")
        except Exception as e:
            print(f"✗ 保存配置文件失败: {e}")
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """深度更新字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        keys = key.split('.')
        config_dict = self.config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config_dict or not isinstance(config_dict[k], dict):
                config_dict[k] = {}
            config_dict = config_dict[k]
        
        config_dict[keys[-1]] = value