# -*- coding: utf-8 -*-
"""
资源路径管理模块
用于处理开发环境和PyInstaller打包后的资源路径
"""

import os
import sys


def get_resource_base_path() -> str:
    """
    获取资源文件的基础路径
    
    Returns:
        资源文件基础路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的环境
        # sys._MEIPASS是PyInstaller临时解压目录
        # 但config.json和language需要在exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bundled_resource_path(relative_path: str) -> str:
    """
    获取打包到exe中的资源路径（如icon、styles）
    
    Args:
        relative_path: 相对路径（如 "icon/icon.png"）
        
    Returns:
        资源文件的完整路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后，使用临时目录中的资源
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_external_resource_path(relative_path: str) -> str:
    """
    获取外部资源路径（如config.json、language目录）
    这些资源应该在exe所在目录，用户可以访问和修改
    
    Args:
        relative_path: 相对路径（如 "config.json"）
        
    Returns:
        资源文件的完整路径
    """
    base_path = get_resource_base_path()
    return os.path.join(base_path, relative_path)
