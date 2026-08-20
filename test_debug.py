import pikepdf
from pathlib import Path

pdf_path = Path(r'F:\52纸模网\工具\No PDF Password\Anubis.pdf')
password = 'paper-replika.com'

print('调试 try_decrypt_pdf 函数...')
print()

try:
    with pikepdf.open(pdf_path, password=password) as pdf:
        print(f'[1] 成功打开PDF')
        print(f'    is_encrypted: {pdf.is_encrypted}')
        print(f'    页数: {len(pdf.pages)}')
        
        page_count = len(pdf.pages)
        
        # 移除加密信息
        print(f'\n[2] 移除加密信息...')
        if pdf.is_encrypted:
            try:
                del pdf.trailer['/Encrypt']
                print(f'    已删除 /Encrypt')
            except KeyError:
                print(f'    /Encrypt 不存在，跳过')
        
        # 保存到临时文件
        temp_path = pdf_path.with_suffix(".pdf.tmp")
        print(f'\n[3] 保存到临时文件: {temp_path}')
        try:
            pdf.save(temp_path, encryption=False)
            print(f'    保存成功')
            
            # 验证临时文件
            print(f'\n[4] 验证临时文件...')
            try:
                with pikepdf.open(temp_path) as verify_pdf:
                    print(f'    成功打开（无密码）')
                    print(f'    is_encrypted: {verify_pdf.is_encrypted}')
                    print(f'    页数: {len(verify_pdf.pages)}')
                    
                    if len(verify_pdf.pages) == page_count:
                        print(f'\n[5] 验证通过，覆盖原文件...')
                        temp_path.replace(pdf_path)
                        print(f'    成功!')
                    else:
                        print(f'\n[5] 页数不匹配，删除临时文件')
                        temp_path.unlink(missing_ok=True)
            except Exception as e:
                print(f'    验证失败: {type(e).__name__}: {e}')
                temp_path.unlink(missing_ok=True)
                
        except Exception as e:
            print(f'    保存失败: {type(e).__name__}: {e}')
            import traceback
            traceback.print_exc()
            temp_path.unlink(missing_ok=True)
            
except pikepdf.PasswordError as e:
    print(f'密码错误: {e}')
except Exception as e:
    print(f'其他错误: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
