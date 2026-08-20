"""
PDF解密诊断脚本
用于诊断解密失败的具体原因
"""

import pikepdf
from pathlib import Path
import sys

def diagnose_pdf(pdf_path: str, password: str):
    """诊断单个PDF文件"""
    path = Path(pdf_path)
    
    print(f"\n{'='*60}")
    print(f"诊断文件: {path.name}")
    print(f"密码: {password}")
    print(f"{'='*60}")
    
    # 1. 检查文件是否存在
    if not path.exists():
        print("[错误] 文件不存在")
        return
    
    print(f"[1] 文件大小: {path.stat().st_size} bytes")
    
    # 2. 尝试不提供密码打开
    print("\n[2] 尝试不提供密码打开...")
    try:
        with pikepdf.open(path) as pdf:
            print(f"  - 成功打开")
            print(f"  - is_encrypted: {pdf.is_encrypted}")
            print(f"  - 页数: {len(pdf.pages)}")
            print(f"  - trailer 有 /Encrypt: {'/Encrypt' in pdf.trailer}")
            if '/Encrypt' in pdf.trailer:
                print(f"  - /Encrypt 内容: {pdf.trailer['/Encrypt']}")
            return  # 能直接打开，说明无密码
    except pikepdf.PasswordError as e:
        print(f"  - PasswordError: {e}")
        print(f"  - 文件确实是加密的")
    except Exception as e:
        print(f"  - 其他错误: {type(e).__name__}: {e}")
        return
    
    # 3. 尝试用提供的密码打开
    print(f"\n[3] 尝试用密码 '{password}' 打开...")
    try:
        with pikepdf.open(path, password=password) as pdf:
            print(f"  - 成功打开!")
            print(f"  - is_encrypted: {pdf.is_encrypted}")
            print(f"  - 页数: {len(pdf.pages)}")
            
            # 4. 检查加密信息
            print(f"\n[4] 检查加密信息...")
            print(f"  - trailer keys: {list(pdf.trailer.keys())}")
            if '/Encrypt' in pdf.trailer:
                encrypt_obj = pdf.trailer['/Encrypt']
                print(f"  - /Encrypt 类型: {type(encrypt_obj)}")
                print(f"  - /Encrypt 内容: {encrypt_obj}")
            
            # 5. 尝试移除加密并保存
            print(f"\n[5] 尝试移除加密并保存...")
            temp_path = path.parent / f"{path.stem}_test_decrypted.pdf"
            
            try:
                # 方法1: 直接删除 /Encrypt
                if '/Encrypt' in pdf.trailer:
                    del pdf.trailer['/Encrypt']
                    print(f"  - 已删除 /Encrypt")
                
                pdf.save(temp_path, encryption=False)
                print(f"  - 保存成功: {temp_path}")
                
                # 6. 验证保存的文件
                print(f"\n[6] 验证保存的文件...")
                with pikepdf.open(temp_path) as verify_pdf:
                    print(f"  - 成功打开（无密码）")
                    print(f"  - is_encrypted: {verify_pdf.is_encrypted}")
                    print(f"  - 页数: {len(verify_pdf.pages)}")
                    
                    if verify_pdf.is_encrypted:
                        print(f"  - [警告] 文件仍然是加密的!")
                    else:
                        print(f"  - [成功] 文件已解密!")
                
                # 清理测试文件
                temp_path.unlink()
                print(f"\n[7] 测试文件已删除")
                
            except Exception as e:
                print(f"  - 保存失败: {type(e).__name__}: {e}")
                temp_path.unlink(missing_ok=True)
                
    except pikepdf.PasswordError as e:
        print(f"  - PasswordError: 密码错误!")
        print(f"  - 错误详情: {e}")
    except Exception as e:
        print(f"  - 其他错误: {type(e).__name__}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python test_decrypt.py <PDF文件路径> <密码>")
        print("示例: python test_decrypt.py \"D:\\资料\\test.pdf\" \"1234\"")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    password = sys.argv[2]
    
    diagnose_pdf(pdf_path, password)
