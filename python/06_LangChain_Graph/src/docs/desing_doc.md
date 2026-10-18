# SYLVAN ホテル トップページ 設計書

## 1. プロジェクト概要

| 項目 | 内容 |
|------|------|
| ホテル名 | SYLVAN |
| コンセプト | 自然感 × リッチ感 — 森の静寂を贅沢として提供するリトリートホテル |
| 対象ページ | トップページ（index.html） |
| 画像使用 | **なし**（CSSのみで視覚表現） |
| 対象ブラウザ | モダンブラウザ全般（Chrome / Firefox / Safari / Edge） |

---

## 2. デザイン方針

### 2.1 デザイントークン（カラーパレット）

| 名称 | HEX | 用途 |
|------|-----|------|
| Charcoal Earth | `#1C1A17` | 背景（ダーク面）、基本文字色 |
| Linen | `#E8DCC8` | 明度の高いテキスト、ヘッダ文字 |
| Aged Brass | `#C9A96E` | アクセント、CTAボタン、装飾線 |
| Forest Moss | `#4A5240` | セカンダリ背景（Experiences, Testimonial） |
| Parchment | `#F5F0E8` | メイン背景（明るい面） |
| Warm Stone | `#7B6E5D` / `#A89880` | サブテキスト、ミュートカラー |

### 2.2 タイポグラフィ

| ロール | フォント | 特徴 |
|--------|----------|------|
| Display（見出し） | Cormorant Garamond | エディトリアル感、細身のセリフ体。重量 300〜600 |
| Body（本文・UI） | Jost | モダンで視認性が高いサンセリフ体。重量 300〜500 |

フォントは Google Fonts より読み込み。フォールバックは `Georgia, serif` / `system-ui, sans-serif`。

### 2.3 シグネチャ要素：「木漏れ日」キャンバスアニメーション

ヒーローセクションの背景として、写真を一切使わず **CSSの重ねたradial-gradientを複数の`<div>`がゆっくり移動する**ことで、樹間を透過する朝の光（木漏れ日）を表現する。

```
3層構造:
  Layer 1: ブラス色・モス色のラジアルグラデーション（18秒サイクル）
  Layer 2: モス色のラジアルグラデーション（24秒サイクル）
  Layer 3: アース色オーバーレイ + 微細なリネン光（30秒サイクル）
```

`@media (prefers-reduced-motion: reduce)` 適用時はアニメーション停止。

---

## 3. ページ構造

```
<header>  サイトヘッダー（固定ナビゲーション）
  └─ ロゴ / ナビリンク / 予約CTA

<section> ヒーロー
  └─ 木漏れ日アニメーション背景 / 大見出し / CTA

<section> Philosophy（#about）
  └─ 引用文 / プロパティ紹介文 / 統計マーカー3点

<section> Rooms（#rooms）
  └─ 3カラムカードグリッド
      ├─ Oak & Moss（Forest Room）
      ├─ Above the Understory（Canopy Suite）★フィーチャーカード
      └─ The Long View（Ridge Villa）

<section> Experiences（#experiences）
  └─ 3体験コンテンツ（交互レイアウト）
      ├─ 夜明けの森林浴
      ├─ 山菜×焚き火ディナー
      └─ 湧き水プール＆サウナ

<section> Testimonial
  └─ 宿泊者レビュー（全幅センタリング）

<section> Contact / Booking（#contact）
  └─ ホテル詳細情報 / お問い合わせフォーム

<footer>  サイトフッター
  └─ ロゴ / 住所 / ナビリンク / コピーライト
```

---

## 4. CSS設計

### 4.1 セクション別背景

| セクション | 背景色 | 文字基調 |
|------------|--------|----------|
| Hero | `#1C1A17` + グラデーションアニメーション | Linen |
| Philosophy | `#1C1A17` | Linen |
| Rooms | `#F5F0E8` | Charcoal Earth |
| Experiences | `#1C1A17` | Linen |
| Testimonial | `#4A5240` | Linen |
| Contact | `#F5F0E8` | Charcoal Earth |
| Footer | `#1C1A17` | Linen |

### 4.2 スクロール連動アニメーション

`IntersectionObserver` を使い、要素がビューポート内に12%以上入った時点で `.is-visible` クラスを付与。

```css
/* 初期状態 */
.reveal { opacity: 0; transform: translateY(32px); transition: 0.9s; }
/* 表示時 */
.reveal.is-visible { opacity: 1; transform: translateY(0); }
```

`reveal-stagger` クラスは複数要素に時差（0.15s, 0.3s）を付けてウェーブ表示。

### 4.3 画像代替のCSS絵（エンブレム・体験ビジュアル）

部屋カードおよびExperiencesセクションに、疑似要素（`::before` / `::after`）のみで構成された抽象的なCSS描写を配置。

| コンポーネント | 表現 |
|----------------|------|
| Room: Circle Emblem | 同心円（border + border-radius:50%）|
| Room: Arc Emblem | 半円アーク + 縦線 |
| Room: Horizon Emblem | グラデーション横線3本（山の稜線） |
| Exp: Dawn Visual | 半円弧（日の出） |
| Exp: Table Visual | 2本横線（長テーブル） |
| Exp: Water Visual | 同心楕円（水面の波紋） |

---

ただし、客室カードのプレースホルダー divは使用禁止。
必ず以下のCSS絵を実装すること：

#### Oak & Moss（Forest Room）- 同心円
```css
.emblem-forest {
  width: 120px; height: 120px;
  margin: 2rem auto;
  position: relative;
  border-radius: 50%;
  border: 2px solid var(--aged-brass);
  box-shadow: 0 0 0 12px rgba(201,169,110,0.1),
              0 0 0 24px rgba(201,169,110,0.06),
              0 0 0 36px rgba(201,169,110,0.03);
}
```

#### Above the Understory（Canopy Suite）- 半円アーク＋縦線
```css
.emblem-canopy {
  width: 120px; height: 60px;
  margin: 2rem auto;
  border-top: 2px solid var(--aged-brass);
  border-left: 2px solid var(--aged-brass);
  border-right: 2px solid var(--aged-brass);
  border-radius: 60px 60px 0 0;
  position: relative;
}
.emblem-canopy::after {
  content: '';
  position: absolute;
  bottom: -40px; left: 50%;
  width: 2px; height: 40px;
  background: var(--aged-brass);
  transform: translateX(-50%);
}
```

#### The Long View（Ridge Villa）- グラデーション横線3本
```css
.emblem-ridge {
  width: 120px;
  margin: 2rem auto;
}
.emblem-ridge span {
  display: block;
  height: 2px;
  margin-bottom: 12px;
  background: linear-gradient(
    to right, transparent, var(--aged-brass), transparent
  );
}
```

## 5. レスポンシブ対応

| ブレークポイント | 変化点 |
|----------------|--------|
| `> 900px` | フルデスクトップレイアウト |
| `≤ 900px` | Experiences・Contact を1カラム化 |
| `≤ 640px` | ナビをドロワーに変更、Rooms・マーカーを縦積み |

---

## 6. アクセシビリティ

- `aria-label` / `aria-labelledby` による意味付け
- `aria-expanded` によるナビトグル状態管理
- `:focus-visible` による視認性の高いフォーカスリング
- `prefers-reduced-motion` 対応（全アニメーション0ms化）
- フォームに `<label for>` 紐付けと `autocomplete` 属性

---

## 7. JavaScript機能

| 機能 | 実装 |
|------|------|
| ヘッダースクロール変化 | `scroll` イベント → `.scrolled` クラス付与 |
| スクロールアニメーション | `IntersectionObserver` → `.is-visible` 付与 |
| モバイルナビ開閉 | `aria-expanded` 制御、Escキー対応、ボディスクロールロック |
| フォーム送信デモ | `submit` イベントでボタンテキスト変更（バックエンド不要） |
| ヒーロー初期表示 | `DOMContentLoaded` + 200ms遅延でフェードイン |
