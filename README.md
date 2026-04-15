# Pixel Agents Viewer

VS Code 拡張 [Pixel Agents](https://marketplace.visualstudio.com/items?itemName=pablodelucca.pixel-agents) のパネルを **ブラウザの独立タブ** で表示するためのランチャーです。

ブラウザ標準の `getDisplayMedia` API（画面共有）を使うので、OBS Studio などの追加ソフトは不要です。

## 仕組み

```
VS Code (Pixel Agents パネル)
        │  画面共有 (getDisplayMedia)
        ▼
ブラウザ タブ (localhost:8765/viewer.html)
        │
        ▼
好きなモニターに配置・全画面化可能
```

- 拡張機能本体は改造しません
- OBS / 仮想カメラ / 外部プラグインは使用しない
- ワンコマンドで VS Code + ローカルHTTPサーバ + ブラウザを起動

## 前提

- Windows 10 / 11
- VS Code + Pixel Agents 拡張 v1.2.0+
- PowerShell 5.1+
- Python 3.9+（ローカル HTTP サーバ用）
- モダンブラウザ（Edge / Chrome）

## 使い方

```powershell
.\launch_browser.ps1
```

処理フロー:
1. VS Code 未起動なら起動
2. ローカル HTTP サーバを `127.0.0.1:8765` で起動（バックグラウンド）
3. 既定ブラウザで `http://127.0.0.1:8765/viewer.html` を開く
4. ページ上の **「画面共有を開始」** をクリック → ダイアログで VS Code ウィンドウを選択

以降、タブを別モニターへドラッグしたり全画面化することで Claude Code セッションを可視化できます。

### 停止

```powershell
.\stop.ps1
```

HTTP サーバを停止します。ブラウザタブと VS Code はそのまま残ります。

## スクリーンショット

| ブラウザビュー | VS Code パネル |
|---|---|
| ![viewer](docs/screenshot-viewer.png) | ![panel](docs/screenshot-panel.png) |

画像を用意するには `docs/` に `Win + Shift + S` で撮影した PNG を置いてください。

## トラブルシュート

| 症状 | 対処 |
|---|---|
| 画面共有ダイアログで VS Code が出てこない | VS Code を起動して再試行 |
| ページを開いても画面が真っ黒 | 「画面共有を開始」ボタンを押す必要あり |
| 共有を途中で止めてしまった | ページを再読込するか、ボタンを再度押す |
| HTTP サーバが起動しない | Python がインストールされているか確認（`python --version`） |

## ライセンス

MIT

## 免責

- Pixel Agents 拡張機能本体は本リポジトリに含まれません。各自で VS Code Marketplace からインストールしてください
