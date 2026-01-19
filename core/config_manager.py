# -*- coding: utf-8 -*-
"""
配置管理器模块
负责 config.json 的读写和更新
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str):
        """
        初始化配置管理器
        
        Args:
            config_path: config.json 文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            加载是否成功
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                return True
            else:
                self.config = self._get_default_config()
                return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
            return False
    
    def save_config(self) -> bool:
        """
        保存配置文件
        
        Returns:
            保存是否成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent='\t', ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "metadata": {
                "version": "v0.1",
                "build_date": "2026.02.01",
                "compatible_version": "4.3.39-beta"
            },
            "localization": {
                "primary_language": "zh_CN",
                "available_languages": ["zh_CN", "en_US"],
                "zh_CN": "中文",
                "en_US": "English"
            },
            "system": {
                "initialized": False,
                "last_loaded": "",
                "link_path": ""
            }
        }
    
    def get_metadata(self) -> Dict[str, str]:
        """获取元数据信息"""
        return self.config.get("metadata", {})
    
    def get_version(self) -> str:
        """获取版本号"""
        return self.config.get("metadata", {}).get("version", "v0.1")
    
    def get_build_date(self) -> str:
        """获取构建日期"""
        return self.config.get("metadata", {}).get("build_date", "")
    
    def get_compatible_version(self) -> str:
        """获取兼容版本"""
        return self.config.get("metadata", {}).get("compatible_version", "")
    
    def get_primary_language(self) -> str:
        """获取主语言"""
        return self.config.get("localization", {}).get("primary_language", "zh_CN")
    
    def set_primary_language(self, language: str) -> None:
        """设置主语言"""
        if "localization" not in self.config:
            self.config["localization"] = {}
        self.config["localization"]["primary_language"] = language
        self.save_config()
    
    def get_available_languages(self) -> List[str]:
        """获取可用语言列表"""
        return self.config.get("localization", {}).get("available_languages", ["zh_CN", "en_US"])
    
    def get_language_display_name(self, language_code: str) -> str:
        """
        获取语言显示名称
        
        Args:
            language_code: 语言代码（如 zh_CN）
            
        Returns:
            显示名称（如 中文）
        """
        return self.config.get("localization", {}).get(language_code, language_code)
    
    def get_initialized(self) -> bool:
        """获取初始化状态"""
        return self.config.get("system", {}).get("initialized", False)
    
    def set_initialized(self, status: bool) -> None:
        """设置初始化状态"""
        if "system" not in self.config:
            self.config["system"] = {}
        self.config["system"]["initialized"] = status
        self.save_config()
    
    def get_last_loaded(self) -> str:
        """获取最后加载时间"""
        return self.config.get("system", {}).get("last_loaded", "")
    
    def set_last_loaded(self, date_str: str) -> None:
        """设置最后加载时间"""
        if "system" not in self.config:
            self.config["system"] = {}
        self.config["system"]["last_loaded"] = date_str
        self.save_config()
    
    def get_link_path(self) -> str:
        """获取链接路径"""
        return self.config.get("system", {}).get("link_path", "")
    
    def set_link_path(self, path: str) -> None:
        """设置链接路径"""
        if "system" not in self.config:
            self.config["system"] = {}
        self.config["system"]["link_path"] = path
        self.save_config()
    
    def update_system_status(self) -> None:
        """更新系统状态（最后加载时间）"""
        if "system" not in self.config:
            self.config["system"] = {}
        self.config["system"]["last_loaded"] = datetime.now().strftime("%Y.%m.%d")
        self.save_config()
