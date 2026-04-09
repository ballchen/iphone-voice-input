# Windows 簡易安裝指南

這份指南提供兩種安裝方式：

- **方式 A（推薦）**：直接使用 Release 的 `.zip`，不需要安裝 Python
- **方式 B（開發者）**：用 Python 原始碼執行

---

## 方式 A：直接執行 Release `.zip`（最簡單）

### Step 1：下載程式

1. 打開 GitHub 專案頁面的 **Releases**
2. 下載最新版本中的 `VoiceInput-windows.zip`
3. 解壓縮後取得 `VoiceInput.exe`

### Step 2：執行程式

1. 雙擊 `VoiceInput.exe`
2. 第一次啟動若看到 Windows 安全性提示，請選擇「仍要執行」
3. 啟動後右下角會出現系統匣圖示（Voice Input）

### Step 3：讓 iPhone 連線

1. 在系統匣圖示上按右鍵
2. 點 **Show QR Code**
3. 用 iPhone 的 Safari 掃描 QR Code
4. 將頁面「加入主畫面」後，日後可像 App 一樣直接開啟

### Step 4：開始輸入

1. 在 Windows 先點選你要輸入文字的視窗（例如 Notepad、瀏覽器、聊天軟體）
2. 在 iPhone 頁面按鍵盤麥克風說話
3. 按「送出到電腦」，文字就會自動打到目前焦點視窗

---

## 方式 B：用 Python 執行（開發者/進階使用）

### Step 1：安裝 Python 3.10+

建議到 Python 官方網站安裝，安裝時勾選 **Add Python to PATH**。

安裝完成後開啟 PowerShell，確認版本：

```powershell
python --version
```

### Step 2：下載專案

```powershell
git clone <your-repo-url>
cd iPhone-voice-input
```

> 若資料夾名稱不同，請改成你的實際路徑。

### Step 3：安裝依賴

```powershell
pip install -r requirements.txt
```

### Step 4：啟動服務

```powershell
python server.py
```

啟動後會看到類似：

```text
[*] Server: http://192.168.x.x:8765
```

同時系統匣會出現圖示，右鍵可顯示 QR Code。

---

## 常見問題排除（Windows）

### 1) iPhone 掃碼後打不開頁面

- 確認 iPhone 與 Windows 在同一個 Wi-Fi
- 先暫時關閉 VPN、公司網路隔離或訪客網路隔離
- 重新啟動 `VoiceInput.exe` 或 `python server.py`

### 2) 可以連線，但文字沒有輸入到目標程式

- 先用滑鼠點一下目標視窗，確保它有焦點
- 再從 iPhone 按「送出到電腦」
- 某些遊戲或高權限程式可能會阻擋模擬鍵盤輸入

### 3) 被 Windows 防火牆擋住

第一次啟動時，若 Windows 跳出防火牆提示，請允許 Python/VoiceInput 在**私人網路**通行。

### 4) 想自己打包 `.exe`（維護者）

在專案根目錄執行：

```powershell
build.bat
```

輸出檔案位置：

```text
dist\VoiceInput.exe
```

### 5) 不想在本機打包，想自動產出 Release ZIP（維護者）

本專案已提供 GitHub Actions 自動流程：

1. 到 GitHub 建立新 Release（例如 tag `v1.0.0`）
2. 推送 tag 後，Actions 會自動在 Windows runner 打包 `VoiceInput.exe`
3. 打包完成後，會自動產生 `VoiceInput-windows.zip` 並附加到該 Release

### 6) 啟動時看到 `Invalid async_mode specified`（舊版 EXE）

這是舊版打包檔漏掉 Socket.IO `threading` driver 的問題。請下載最新版 Release ZIP（`v1.0.1` 以上）並重新解壓執行。
