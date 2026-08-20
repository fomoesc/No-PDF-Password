"""
配置管理模块
负责读写JSON配置（预设密码列表、上次扫描路径）
"""

import json
from pathlib import Path
from typing import List


class ConfigManager:
    """配置管理器，负责读写配置文件"""
    
    DEFAULT_CONFIG = {
        "passwords": ["paper-replika.com"],
        "last_scan_path": ""
    }
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            # 默认配置文件路径：与main.py同目录
            config_path = Path(__file__).parent.parent / "config.json"
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件，不存在则创建默认配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 确保必要字段存在
                if "passwords" not in config:
                    config["passwords"] = self.DEFAULT_CONFIG["passwords"]
                if "last_scan_path" not in config:
                    config["last_scan_path"] = self.DEFAULT_CONFIG["last_scan_path"]
                return config
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: dict = None):
        """保存配置到文件"""
        if config is None:
            config = self._config
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except IOError as e:
            raise IOError(f"无法保存配置文件：{e}")
    
    def get_passwords(self) -> List[str]:
        """获取预设密码列表"""
        return self._config.get("passwords", [])
    
    def add_password(self, password: str) -> bool:
        """添加密码，返回是否成功（已存在则返回False）"""
        if password in self._config["passwords"]:
            return False
        self._config["passwords"].append(password)
        self._save_config()
        return True
    
    def remove_password(self, password: str) -> bool:
        """删除密码，返回是否成功（不存在则返回False）"""
        if password in self._config["passwords"]:
            self._config["passwords"].remove(password)
            self._save_config()
            return True
        return False
    
    def get_last_scan_path(self) -> str:
        """获取上次扫描路径"""
        return self._config.get("last_scan_path", "")
    
    def set_last_scan_path(self, path: str):
        """设置上次扫描路径"""
        self._config["last_scan_path"] = path
        self._save_config()
