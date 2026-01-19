# -*- coding: utf-8 -*-
"""
文件转换工具模块
封装 txt_to_json、key_names_format、json_to_txt 的处理逻辑
"""

import json
import os
import shutil
from typing import Optional, Tuple

from .key_constants import KEY_TO_CHAR, CHAR_TO_KEY, VALID_MODIFIERS


class FileConverter:
    """文件转换工具类"""
    
    @staticmethod
    def validate_hotkey_file(file_path: str) -> Tuple[bool, str]:
        """
        校验快捷键文件是否有效
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        if not file_path.lower().endswith('.txt'):
            return False, "文件扩展名必须为 .txt"
        
        basename = os.path.basename(file_path).lower()
        if 'hotkeys' not in basename:
            return False, "文件名必须包含 'hotkeys'"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line != '--- General ---':
                    return False, "文件首行必须为 '--- General ---'"
        except Exception as e:
            return False, f"读取文件失败: {str(e)}"
        
        return True, ""
    
    @staticmethod
    def txt_to_json(input_path: str, output_path: str) -> bool:
        """
        将快捷键文本文件转换为 JSON 格式
        
        Args:
            input_path: 输入的 txt 文件路径
            output_path: 输出的 json 文件路径
            
        Returns:
            转换是否成功
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            categories = []
            current_category = None
            current_items = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('---') and line.endswith('---'):
                    if current_category is not None:
                        categories.append({
                            "categoryId": current_category,
                            "items": current_items
                        })
                    current_category = line.strip('-').strip()
                    current_items = []
                elif line and ':' in line:
                    parts = line.split(':', 1)
                    command_id = parts[0].strip()
                    shortcut = parts[1].strip()
                    
                    existing_item = None
                    for item in current_items:
                        if item["commandId"] == command_id:
                            existing_item = item
                            break
                    
                    if existing_item:
                        if shortcut and shortcut not in existing_item["shortcuts"]:
                            existing_item["shortcuts"].append(shortcut)
                    else:
                        shortcuts = [shortcut] if shortcut else []
                        current_items.append({
                            "commandId": command_id,
                            "shortcuts": shortcuts
                        })
            
            if current_category is not None:
                categories.append({
                    "categoryId": current_category,
                    "items": current_items
                })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            raise Exception(f"txt_to_json 转换失败: {str(e)}")
    
    @staticmethod
    def _parse_and_format_shortcut(shortcut_str: str) -> Optional[str]:
        """
        解析并格式化快捷键字符串
        
        Args:
            shortcut_str: 原始快捷键字符串
            
        Returns:
            格式化后的快捷键字符串，无效则返回 None
        """
        if not shortcut_str:
            return None
        
        parts = []
        buffer = ""
        in_quote = False
        
        for char in shortcut_str:
            if char == "'":
                in_quote = not in_quote
                buffer += char
            elif char == '+' and not in_quote:
                parts.append(buffer)
                buffer = ""
            else:
                buffer += char
        parts.append(buffer)
        
        clean_parts = []
        for p in parts:
            stripped = p.strip()
            if not stripped:
                return None
            clean_parts.append(stripped)
        
        if not clean_parts:
            return None
        
        key_raw = clean_parts[-1]
        modifiers_raw = clean_parts[:-1]
        
        processed_modifiers = set()
        for mod in modifiers_raw:
            mod_lower = mod.lower()
            if mod_lower not in VALID_MODIFIERS:
                return None
            processed_modifiers.add(mod_lower)
        
        final_key = key_raw
        
        if final_key.startswith("'") and final_key.endswith("'"):
            if len(final_key) < 2:
                return None
            
            content = final_key[1:-1]
            
            if content in KEY_TO_CHAR:
                content = KEY_TO_CHAR[content]
            
            final_key = f"'{content}'"
            
            if 'ctrl' in processed_modifiers or 'shift' in processed_modifiers:
                return None
            
            if ' ' in content and len(content) > 1:
                return None
        else:
            if final_key in CHAR_TO_KEY:
                final_key = CHAR_TO_KEY[final_key]
            
            if final_key.lower() in VALID_MODIFIERS:
                return None
            
            if '"' in final_key or "'" in final_key:
                return None
        
        sorted_modifiers = []
        if 'ctrl' in processed_modifiers:
            sorted_modifiers.append('ctrl')
        if 'shift' in processed_modifiers:
            sorted_modifiers.append('shift')
        if 'alt' in processed_modifiers:
            sorted_modifiers.append('alt')
        
        if sorted_modifiers:
            return f"{' + '.join(sorted_modifiers)} + {final_key}"
        else:
            return final_key
    
    @staticmethod
    def format_key_names(input_path: str, output_path: str) -> bool:
        """
        格式化 JSON 中的快捷键名称
        
        Args:
            input_path: 输入的 json 文件路径
            output_path: 输出的 json 文件路径
            
        Returns:
            处理是否成功
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for category in data:
                for item in category.get('items', []):
                    seen = set()
                    unique_shortcuts = []
                    
                    raw_shortcuts = item.get('shortcuts', [])
                    
                    for shortcut in raw_shortcuts:
                        formatted = FileConverter._parse_and_format_shortcut(shortcut)
                        
                        if formatted:
                            if formatted not in seen:
                                seen.add(formatted)
                                unique_shortcuts.append(formatted)
                    
                    item['shortcuts'] = unique_shortcuts
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            raise Exception(f"format_key_names 处理失败: {str(e)}")
    
    @staticmethod
    def json_to_txt(input_path: str, output_path: str) -> bool:
        """
        将 JSON 格式转换回快捷键文本文件
        
        Args:
            input_path: 输入的 json 文件路径
            output_path: 输出的 txt 文件路径
            
        Returns:
            转换是否成功
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                categories = json.load(f)
            
            output_lines = []
            for i, category in enumerate(categories):
                output_lines.append(f"--- {category['categoryId']} ---")
                for item in category['items']:
                    command_id = item['commandId']
                    shortcuts = item['shortcuts']
                    
                    if shortcuts:
                        for shortcut in shortcuts:
                            output_lines.append(f"{command_id}: {shortcut}")
                    else:
                        output_lines.append(f"{command_id}: ")
                
                if i < len(categories) - 1:
                    output_lines.append("")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(output_lines))
            
            return True
        except Exception as e:
            raise Exception(f"json_to_txt 转换失败: {str(e)}")
    
    @staticmethod
    def import_and_process(txt_path: str, processing_dir: str) -> str:
        """
        执行完整的导入和预处理流程
        
        Args:
            txt_path: 原始 txt 文件路径
            processing_dir: 处理目录路径
            
        Returns:
            处理后的 json 文件路径
            
        Raises:
            Exception: 处理过程中的任何错误
        """
        os.makedirs(processing_dir, exist_ok=True)
        
        basename = os.path.basename(txt_path)
        copied_txt = os.path.join(processing_dir, basename)
        shutil.copy2(txt_path, copied_txt)
        
        temp_json = os.path.join(processing_dir, 'hotkeys_temp.json')
        final_json = os.path.join(processing_dir, 'hotkeys.json')
        
        FileConverter.txt_to_json(copied_txt, temp_json)
        FileConverter.format_key_names(temp_json, final_json)
        
        if os.path.exists(temp_json):
            os.remove(temp_json)
        
        return final_json
