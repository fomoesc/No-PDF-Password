"""
PDF解密核心模块
负责递归扫描文件夹、用密码尝试解锁、先验证再覆盖保存
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
import pikepdf


class PDFStatus(Enum):
    """PDF处理状态"""
    NO_PASSWORD = "no_password"      # 无密码，无需处理
    DECRYPTED = "decrypted"          # 已成功解锁
    NEED_MANUAL = "need_manual"      # 预设密码均失败，需手动处理
    ERROR = "error"                  # 文件损坏或其他错误


@dataclass
class PDFResult:
    """PDF处理结果"""
    file_path: Path
    status: PDFStatus
    password_used: Optional[str] = None  # 使用的密码（仅DECRYPTED状态）
    error_msg: Optional[str] = None      # 错误信息（仅ERROR状态）


def scan_pdf_files(folder_path: Path) -> List[Path]:
    """
    递归扫描文件夹，找出所有PDF文件
    
    Args:
        folder_path: 要扫描的文件夹路径
        
    Returns:
        所有PDF文件路径列表
    """
    pdf_files = []
    try:
        for item in folder_path.rglob("*.pdf"):
            if item.is_file():
                pdf_files.append(item)
    except PermissionError:
        pass  # 跳过无权限访问的目录
    return sorted(pdf_files)


def check_pdf_encrypted(pdf_path: Path) -> bool:
    """
    检查PDF是否加密
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        True表示加密，False表示无密码
    """
    try:
        with pikepdf.open(pdf_path) as pdf:
            # 如果能直接打开且没有加密标记，则无密码
            return pdf.is_encrypted
    except pikepdf.PasswordError:
        return True
    except Exception:
        return True  # 其他错误保守认为是加密


def try_decrypt_pdf(pdf_path: Path, password: str) -> bool:
    """
    尝试用指定密码解密PDF，成功则覆盖保存
    
    Args:
        pdf_path: PDF文件路径
        password: 尝试的密码
        
    Returns:
        True表示解密成功并保存，False表示密码错误或失败
    """
    try:
        with pikepdf.open(pdf_path, password=password) as pdf:
            # 解密成功，验证PDF结构完整性
            # 尝试读取页数来验证文件完整性
            page_count = len(pdf.pages)
            if page_count == 0:
                return False  # 空PDF视为失败
            
            # 先保存到临时文件，验证无误后再覆盖
            temp_path = pdf_path.with_suffix(".pdf.tmp")
            try:
                pdf.save(temp_path)
                
                # 验证临时文件可以正常打开
                with pikepdf.open(temp_path) as verify_pdf:
                    if len(verify_pdf.pages) == page_count:
                        # 验证通过，覆盖原文件
                        temp_path.replace(pdf_path)
                        return True
                    else:
                        # 页数不匹配，删除临时文件
                        temp_path.unlink(missing_ok=True)
                        return False
            except Exception:
                # 保存或验证失败，删除临时文件
                temp_path.unlink(missing_ok=True)
                return False
                
    except pikepdf.PasswordError:
        return False  # 密码错误
    except Exception:
        return False  # 其他错误


def process_single_pdf(pdf_path: Path, passwords: List[str]) -> PDFResult:
    """
    处理单个PDF文件
    
    Args:
        pdf_path: PDF文件路径
        passwords: 预设密码列表
        
    Returns:
        处理结果
    """
    # 先检查是否加密
    if not check_pdf_encrypted(pdf_path):
        return PDFResult(file_path=pdf_path, status=PDFStatus.NO_PASSWORD)
    
    # 尝试每个密码
    for password in passwords:
        if try_decrypt_pdf(pdf_path, password):
            return PDFResult(
                file_path=pdf_path,
                status=PDFStatus.DECRYPTED,
                password_used=password
            )
    
    # 所有密码都失败
    return PDFResult(file_path=pdf_path, status=PDFStatus.NEED_MANUAL)


def decrypt_with_password(pdf_path: Path, password: str) -> Tuple[bool, str]:
    """
    用指定密码手动解密PDF（用于手动处理）
    
    Args:
        pdf_path: PDF文件路径
        password: 用户提供的密码
        
    Returns:
        (成功与否, 消息)
    """
    if try_decrypt_pdf(pdf_path, password):
        return True, "解密成功"
    else:
        return False, "密码错误或文件损坏"
