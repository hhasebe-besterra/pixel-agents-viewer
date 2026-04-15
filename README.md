# Pixel Agents Viewer

VS Code 拡張 [Pixel Agents](https://marketplace.visualstudio.com/items?itemName=pablodelucca.pixel-agents) のパネルを **独立した常時最前面ウィンドウ** として表示するためのランチャーです。

Claude Code セッションを「ピクセルオフィスで働くキャラクター」として可視化できる Pixel Agents 拡張は、標準では VS Code 内部パネルにしか表示されません。本ツールは OBS Studio の Windowed Projector 機能を使い、その表示領域を独立ウィンドウとしてクローンします。

## スクリーンショット

| Projector | VS Code パネル |
|---|---|
| ![projector](docs/screenshot-projector.png) | ![panel](docs/screenshot-panel.png) |

> 画像を用意するには `docs/` フォルダを作成し、任意のスクリーンショットツール（Windows: `Win + Shift + S`）で Projector ウィンドウと VS Code パネルをそれぞれ PNG で保存してください。

## 仕組み

```
VS Code (Pixel Agents パネル)
        │ ウィンドウキャプチャ
        ▼
OBS Studio (ヘッドレス起動)
        │ Windowed Projector
        ▼
独立ウィンドウ（別モニターに配置可 / 常時最前面化可）
```

- 拡張機能本体は改造しません（更新耐性あり）
- OBS WebSocket 経由でシーン・ソース・プロジェクターを自動生成
- ワンクリックで起動／停止

## 前提

- Windows 10 / 11
- VS Code + Pixel Agents 拡張 v1.2.0+（すでに Pixel Agents パネルを使える状態）
- PowerShell 5.1+
- Python 3.9+（`obsws-python` インストール用）
- `winget` 利用可能

## セットアップ（初回のみ）

管理者権限 PowerShell で以下を実行:

```powershell
.\setup.ps1
```

実行内容:
1. OBS Studio を winget でインストール（未インストール時のみ）
2. OBS WebSocket をポート 4455・パスワード `pixelagents` で有効化
3. `obsws-python` を pip インストール

## 日常起動

VS Code を開いて Pixel Agents パネルを表示した状態で:

```powershell
.\launch.ps1
```

処理フロー:
1. OBS をヘッドレス起動（システムトレイに常駐）
2. WebSocket 経由でシーン `PixelAgents` とウィンドウキャプチャソースを作成
3. VS Code ウィンドウを自動検出してキャプチャ
4. Windowed Projector を開く → 独立ウィンドウ表示

独立ウィンドウはドラッグで別モニターに移動できます。

## 停止

```powershell
.\stop.ps1
```

OBS プロセスを終了し、Projector ウィンドウも閉じます。

## カスタマイズ

### クロップ範囲の調整

OBS ウィンドウ（タスクトレイから復帰）で `PixelAgents` シーンの Window Capture ソースを右クリック → Transform → Edit Transform でクロップを調整できます。調整結果は OBS の scene collection に保存され、次回以降も有効です。

### ウィンドウ位置・サイズの記憶

`.\stop.ps1` 実行時に Projector ウィンドウの現在位置・サイズを `geometry.json` に保存します。次回 `.\launch.ps1` ではその値で復元されます。`geometry.json` は `.gitignore` 対象（個人設定扱い）。削除すればデフォルト（100, 100, 960×720）に戻ります。

### 常時最前面表示

OBS の Windowed Projector ウィンドウのタイトルバー右クリック → "Always on Top" をチェック。

### 複数モニター活用

Projector ウィンドウをサブモニターにドラッグして配置。VS Code をメインモニターで使いつつ、サブモニターで Claude Code セッションの様子を常時可視化できます。

## トラブルシュート

| 症状 | 対処 |
|---|---|
| WebSocket 接続に失敗 | OBS が完全起動してから再試行。初回は 10 秒程度かかる |
| VS Code が検出されない | VS Code を起動してから `launch.ps1` を実行 |
| Projector が真っ黒 | OBS ウィンドウでソースを Window Capture Method = Windows Graphics Capture に変更 |
| OBS WebSocket を無効にしたい | `%APPDATA%\obs-studio\plugin_config\obs-websocket\config.json` の `server_enabled` を `false` に |

## ライセンス

MIT

## 免責

- Pixel Agents 拡張機能本体は本リポジトリに含まれません。各自で VS Code Marketplace からインストールしてください
- OBS Studio は OBS Project のもので、GPL v2 ライセンスで配布されています
