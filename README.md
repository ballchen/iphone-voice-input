# iPhone Voice Input

用 iPhone 語音辨識將文字輸入到 Windows 電腦的任意視窗。

## 安裝教學

- Windows 一鍵/簡易安裝請看：[`WINDOWS_INSTALL_GUIDE.md`](./WINDOWS_INSTALL_GUIDE.md)

## 功能

- iPhone 加入主畫面，像 native app 一樣使用（PWA）
- 說話後文字透過 WebSocket 傳到 Windows，自動模擬鍵盤輸入
- 支援「送出後按 Enter」開關
- Windows 系統匣圖示，右鍵顯示 QR Code 讓 iPhone 掃碼連線

## 環境需求

- Windows 10 / 11
- Python 3.10+
- iPhone 與電腦在同一個 Wi-Fi 網路

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 直接執行

```bash
python server.py
```

右下角出現系統匣圖示後，右鍵 → **Show QR Code**，用 iPhone Safari 掃描。

### 3. 打包成 .exe（選用）

```bash
build.bat
```

產生 `dist/VoiceInput.exe`，雙擊即可執行，不需安裝 Python。

## iPhone 設定（第一次）

1. Safari 掃 QR Code 進入網頁
2. 點下方分享按鈕 → **加入主畫面**
3. 之後直接從主畫面開啟

## 使用方式

1. 開啟 app，確認右上角顯示「已連線」
2. 點文字框，按 iOS 鍵盤上的**麥克風**說話
3. 確認文字後按**送出到電腦**
4. 文字會輸入到 Windows 目前焦點的視窗

## 外網使用（選用）

如果想在不同 Wi-Fi 環境下使用，可搭配 Cloudflare Tunnel：

```bash
cloudflared tunnel --url http://localhost:8765
```

## 授權

MIT
