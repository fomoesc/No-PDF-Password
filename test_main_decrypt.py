from src.pdf_decryptor import *
from pathlib import Path

pdf_path = Path(r'F:\52纸模网\工具\No PDF Password\Anubis.pdf')
password = 'paper-replika.com'

print('测试主程序解密函数...')
print()

# 测试 check_pdf_encrypted
print('1. 检查是否加密:')
is_encrypted = check_pdf_encrypted(pdf_path)
print(f'   结果: {is_encrypted}')

# 测试 try_decrypt_pdf
print()
print('2. 尝试解密:')
result = try_decrypt_pdf(pdf_path, password)
print(f'   结果: {result}')

# 测试 process_single_pdf
print()
print('3. 完整处理流程:')
process_result = process_single_pdf(pdf_path, [password])
print(f'   状态: {process_result.status}')
print(f'   使用的密码: {process_result.password_used}')
