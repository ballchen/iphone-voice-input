# iPhone Voice Input

用 iPhone 語音辨識將文字輸入到 Windows 電腦的任意視窗。

## 安裝教學

- Windows 一鍵/簡易安裝請看：[`WINDOWS_INSTALL_GUIDE.md`](./WINDOWS_INSTALL_GUIDE.md)
- 使用者直接下載：到 GitHub **Releases** 下載 `VoiceInput-windows.zip`

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

## 發布流程（自動上傳 ZIP 到 Release）

此專案已設定 GitHub Actions：當你 push 版本 tag（例如 `v1.0.0`）後，會自動：

1. 在 Windows runner 安裝依賴
2. 用 PyInstaller 打包 `VoiceInput.exe`
3. 將 `VoiceInput.exe` 打包成 `VoiceInput-windows.zip`
4. 自動建立（或更新）該 tag 的 GitHub Release
5. 把 `VoiceInput-windows.zip` 附加到該 Release

> 打包時會強制包含 `engineio.async_drivers.threading`，
> 避免 Windows 執行檔出現 `Invalid async_mode specified`。

Workflow 檔案位置：

```text
.github/workflows/release-windows-exe.yml
```

維護者使用方式：

1. Push 程式碼到 `main`
2. 建立並 push tag（例如 `v1.0.0`）
3. 推送 tag 到遠端：`git push origin v1.0.0`
4. 等待 GitHub Actions 完成
5. 到該 Release 的 Assets 下載 `VoiceInput-windows.zip`

## iPhone 設定（第一次）

1. Safari 掃 QR Code 進入網頁
2. 點下方分享按鈕 → **加入主畫面**
3. 之後直接從主畫面開啟

## 使用方式

1. 開啟 app，確認右上角顯示「已連線」
2. 點文字框，按 iOS 鍵盤上的**麥克風**說話
3. 確認文字後按**送出到電腦**
4. 文字會輸入到 Windows 目前焦點的視窗

> 輸入優先採用強制貼上（Clipboard + Ctrl+V / Shift+Insert），
> 可避開注音/拼音輸入法的鍵盤組字干擾；若失敗才會 fallback。

## 連線疑難排解（QR 掃了打不開）

若 iPhone 掃 QR 後打不開頁面，請依序確認：

1. 先在 Windows 防火牆允許 `VoiceInput.exe`（或 Python）於**私人網路**
2. 在系統匣右鍵改用其他 `Show QR Code (<ip>)` 項目（若有多個 IP）
3. 用 **Copy All URLs**，把網址貼到 iPhone Safari 手動開啟測試
4. iPhone 關閉「私人 Wi-Fi 位址」後重連該 Wi-Fi 再試一次
5. 先暫時關掉 VPN / Proxy / 網路隔離功能（手機與電腦都要）
6. 在系統匣選單點 **Open Local Test Page** 測試 `http://127.0.0.1:8765`
   - 若本機都打不開，代表 HTTP server 啟動失敗，請改用最新版 Release 重試
7. 若 Console 出現 `io is not defined` 或 `socket.io 400`，請更新到最新版 Release（已改為內建 Socket.IO client script，並修正初始化順序）

## 外網使用（選用）

如果想在不同 Wi-Fi 環境下使用，可搭配 Cloudflare Tunnel：

```bash
cloudflared tunnel --url http://localhost:8765
```

## 授權

MIT
