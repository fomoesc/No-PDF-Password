# No PDF Password

PDF批量解锁工具。自动遍历文件夹中所有PDF文件，用预设密码库批量解锁，支持手动输入密码处理顽固文件。

## 功能特点

- ✅ **递归扫描**：自动遍历所有子文件夹，不管嵌套多少层
- ✅ **静默解密**：自动调用密码库逐一尝试，无需人工干预
- ✅ **安全覆盖**：先验证PDF完整性，再覆盖原文件，不会损坏
- ✅ **进度显示**：实时显示扫描和处理进度
- ✅ **手动处理**：双击待处理文件，弹窗输入密码
- ✅ **密码库管理**：独立选项卡，增删改密码
- ✅ **记住路径**：下次打开自动载入上次扫描目录
- ✅ **跨平台**：支持 macOS 和 Windows

## 下载安装

### macOS
1. 下载 `No PDF Password`（无扩展名）
2. 双击运行（首次可能需要在"系统偏好设置 > 安全性与隐私"中允许运行）

### Windows
1. 下载 `No PDF Password.exe`
2. 双击运行

## 使用方法

1. **打开软件**
2. **点击"选择文件夹"** → 选择包含PDF的文件夹
3. **点击"开始解密"** → 工具自动扫描并处理所有PDF
4. **查看结果**：
   - ✅ 已删除密码 → 音频处理完成
   - ⏭ 无密码 → 无需处理
   - ❌ 待手动处理 → 双击该文件，输入密码解锁
5. **管理密码库**：切换到"密码库"选项卡，可添加或删除预设密码

## 默认密码

软件首次运行时，密码库中包含一个默认密码：
- `paper-replika.com`

你可以随时在"密码库"选项卡中添加更多密码。

## 从源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

## 打包

### macOS
```bash
chmod +x build_mac.sh
./build_mac.sh
```

### Windows
双击 `build_windows.bat`

## GitHub Actions 自动构建

推送 `v` 开头的标签（如 `v1.0.0`）会自动触发构建，生成 macOS 和 Windows 两个版本的安装包。

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 技术栈

- Python 3.10+
- PySide6（GUI）
- pikepdf（PDF处理）
- PyInstaller（打包）

## 许可证

MIT License
