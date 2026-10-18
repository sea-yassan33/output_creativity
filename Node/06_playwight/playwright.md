# playwrightについて

- https://playwright.dev/

## 参考
- https://qiita.com/tanaka_taro_JP_KYUSYU/items/a194f6132e81bf472981

## playwrightとは

- Microsoftが開発したWebブラウザの自動操作およびE2E（エンドツーエンド）テストを効率化するオープンソースのフレームワークです。
- Windows、Linux、macOS上でChromium、WebKit、Firefoxをサポートしています。
- ローカル環境でもCI環境でも、ヘッドレス環境でもヘッド付き環境でも実行可能です。
- Chrome（Android）とMobile Safariのネイティブモバイルエミュレーションにも対応しています。

## E2Eテストと課題

- Selenium
  - 最も古くから使われてきた定番ツール
  - 多くのブラウザに対応しています
  - セットアップが複雑で動作が不安定になりやすい
- Puppeteer
  - ChromeをヘッドレスモードでNode.jsから操作できます。
  - Chrome（Chromium）専用で、FirefoxやSafariには対応していません。
- Cypress
  - Chrome系ブラウザのみ対応で、iframeや複数タブ操作に弱い面がありました。

## Playwrightが解決したこと

|課題|Playwright の解決策|
|:----|:----|
|ブラウザが限定される|Chromium・Firefox・WebKitを1つのAPIで操作|
|テストが不安定（Flaky）|auto-wait機能で要素が操作可能になるまで自動待機|
|セットアップが複雑|npm init playwright@latest 1コマンドで完了|
|並列実行がしにくい|ワーカーによる並列テスト実行を標準サポート|
|デバッグが難しい|Trace Viewer / UI Mode などの強力なデバッグ機能|

- 最大の特徴： auto-wait機能で要素が操作可能になるまで自動待機

```js
await page.click('#submit-button')
// ← sleepなし！要素が操作可能になるまで自動で待ってくれる
await page.fill('#result', 'done')
```

- Playwrightは内部で以下のすべてを自動チェック
  - 要素がDOMに存在するか？
  - 要素が画面に表示されているか？
  - 要素が操作可能（クリックできる）状態か？
  - アニメーションが完了しているか？

## 便利な機能

- コードジェネレーター（codegen）
  - ブラウザを手動操作するだけでテストコードを自動生成

```sh
npx playwright codegen https://example.com
```

- Trace Viewer（トレースビューア）
  - テストが失敗したとき、操作のすべての過程を録画したトレースファイル

```sh
npx playwright show-report
```

トレースビューアでは以下が確認できます。
  - 各ステップのスクリーンショット
  - ネットワークリクエスト
  - コンソールログ
  - DOMの状態

- UI Mode
  - version1.32で追加されたインタラクティブなテスト実行画面
  - テストをGUI上で1件ずつ実行できる
  - ステップごとにブラウザの状態を確認できる
  - ホットリロードでコード変更が即反映される

- スクリーンショット・動画の自動保存

- APIテストも同じコードで書ける

## 導入

```sh
npm init playwright@latest

Getting started with writing end-to-end tests with Playwright:
Initializing project in '.'
√ Do you want to use TypeScript or JavaScript? · TypeScript
√ Where to put your end-to-end tests? · tests
√ Add a GitHub Actions workflow? (Y/n) · false
√ Install Playwright browsers (can be done manually via 'npx playwright install')? (Y/n) · false
Initializing NPM project (npm init -y)…

## typescript導入
npm install --save-dev typescript
npx tsc --init

## dotenv導入
npm i --save-dev dotenv

npm install --save-dev cross-env

## 全部ブラウザ（1GB程）
npx playwright install

## Chromiumのみ
npx playwright install chromium

## FireFoxのみ
npx playwright install firefox

## WebKit(safariベース)のみ
npx playwright install webkit
```

## tsconfig.jsonを編集
```json
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "commonjs",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "types": ["node"]
  }
}
```

指示が表示されたら、選択／確認してください。

TypeScriptまたはJavaScript（デフォルト：TypeScript）
テストフォルダ名（デフォルト：tests、または既に存在するe2e場合tests）
GitHub Actionsワークフローを追加する（CIに推奨）
Playwrightブラウザをインストールする（デフォルト：はい）

## ブラウザを操作してコードを自動生成

```sh
## 利用可能なオプション
npx playwright codegen --help

## SP（Pixel 5） 
npx playwright codegen --device="Pixel 5" https://example.com/

## SSL証明認証をoff
npx playwright codegen --ignore-https-errors https://example.com/

## 画面サイズを指定する場合
npx playwright codegen --viewport-size=375,812 https://example.com/
```

## テスト実行コマンド

```sh
# すべてのテストを実行
npx playwright test

# 特定のファイルだけ実行
npx playwright test tests/sample.spec.ts

# Chromiumのブラウザを表示してテスト実行
npx playwright test tests/sample.spec.ts --headed --project=chromium

```

## テストから結果をCSVに出力までのテストコード

> 関数

- tests\utils\commonUtil.ts

```ts
// ───── 共通関数 ─────
//  現在日時から 'YYYYMMDD-hhmm' 形式の文字列を生成する関数
export function getFormattedTimestamp(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  return `${year}${month}${day}-${hours}${minutes}`;
}

// log出力・logList格納
export function logger(logList: string[], message: string) {
  const time = new Date().toISOString();
  const cleanMessage = message.replace(/^\n+/, "");
  const formattedMessage = `[${time}] ${cleanMessage}`;
  console.log(message); // 標準ターミナルに出力
  logList.push(formattedMessage); // ログ用バッファに保存
  return logList;
}
```

> 型定義

- tests\typs\testTypes.ts

```ts
// ───── 型定義 ─────
// アクション
export type Action =
  | { type: "clickRole"; role: "button" | "link"; name: string }
  | { type: "clickSelector"; selector: string }
  | { type: "fill"; selector: string; value: string }
  | { type: "check"; selector: string }
  | { type: "selectOption"; selector: string; value: string }
  | { type: "wait"; timeoutMs: number };
// テストケース
export interface TestCase {
  name: string;
  startPath: string;
  actions: Action[];
  expectedPath: string;
}
// CSV出力
export interface TestResult {
  testName: string;
  finalUrl: string;
  status: "SUCCESS" | "FAILED";
  errorMessage: string;
  timestamp: string;
}
```

> テストケース

- tests\case\sample01.ts

```ts
import { TestCase } from "../typs/testTypes";
// ───── テストケース ─────
export const testCases: TestCase[] = [
  {
    name: "遷移確認1",
    startPath: "/",
    actions: [
      { type: "clickRole", role: "button", name: "メニューを開く" },
      { type: "clickRole", role: "link", name: "サイトマップ" },
    ],
    expectedPath: "/sitemap_page",
  },
  {
    name: "遷移確認2",
    startPath: "/",
    actions: [
      { type: "clickRole", role: "button", name: "メニューを開く" },
      { type: "clickRole", role: "link", name: "リンク" },
    ],
    expectedPath: "/links",
  },
  /**{
    name: "フォーム入力・送信遷移（例）",
    startPath: "/contact",
    actions: [
      { type: "fill", selector: "#name", value: "テスト太郎" },
      { type: "fill", selector: "#email", value: "test@example.com" },
      { type: "clickRole", role: "button", name: "送信する" },
    ],
    expectedPath: "/contact/thanks",
  },
  **/
];
```

> テスト実行の本体

- tests\sample.spec.ts

```ts
import { test, expect, devices } from "@playwright/test";
import dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";
import { TestCase, TestResult } from "./typs/testTypes";
import { getFormattedTimestamp, logger } from "./utils/commonUtil";
dotenv.config();
// ───── テストケース読み込み ─────
const targetFile = process.env.TEST_FILE || "./tests/case/sample01.ts";
const resolvedPath = path.resolve(process.cwd(), targetFile);
if (!fs.existsSync(resolvedPath)) {
  throw new Error(
    `[エラー] 指定されたテストファイルが存在しません: ${resolvedPath}`,
  );
}
const { testCases }: { testCases: TestCase[] } = require(resolvedPath);
if (!Array.isArray(testCases)) {
  throw new Error(
    `[エラー] ${targetFile} 内でtestCasesが正しくexportされていません。`,
  );
}
// ───── 定数 ─────
// ログ収集配列
const logList: string[] = [];
// 全テスト結果を保持する配列
const results: TestResult[] = [];
// テストデバイス・オプション設定
test.use({
  ...devices["Pixel 5"], // デバイス指定
  ignoreHTTPSErrors: true, // SSL証明書エラー無視
});
// ───── テスト実行 ─────
test.describe("Sampleテスト", () => {
  testCases.forEach((tc, index) => {
    test(tc.name, async ({ page }) => {
      logger(
        logList,
        `\n【${tc.name}】test(${index + 1}/${testCases.length})...`,
      );
      try {
        // 開始ページへ移動
        await page.goto(`${process.env.DOMEIN}${tc.startPath}`);
        // 定義された操作ステップを順番に実行
        for (const action of tc.actions) {
          switch (action.type) {
            case "clickRole":
              await page.getByRole(action.role, { name: action.name }).click();
              break;
            case "clickSelector":
              await page.click(action.selector);
              break;
            case "fill":
              await page.fill(action.selector, action.value);
              break;
            case "check":
              await page.check(action.selector);
              break;
            case "selectOption":
              await page.selectOption(action.selector, action.value);
              break;
            case "wait":
              await page.waitForTimeout(action.timeoutMs);
              break;
          }
        }
        // 最終URLの検証
        await expect(page).toHaveURL(`${process.env.DOMEIN}${tc.expectedPath}`);
        results.push({
          testName: tc.name,
          finalUrl: page.url(),
          status: "SUCCESS",
          errorMessage: "",
          timestamp: getFormattedTimestamp(),
        });
      } catch (error: any) {
        results.push({
          testName: tc.name,
          finalUrl: page.url(),
          status: "FAILED",
          errorMessage: error.message.replace(/\n/g, " "),
          timestamp: getFormattedTimestamp(),
        });
      }
    });
  });
  // 結果をCSV形式で出力
  test.afterAll(async () => {
    const outputDir = path.join(process.cwd(), "./tests/result");
    if (!fs.existsSync(outputDir)) {
      // 対象ディレクト作成
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const timestampStr = getFormattedTimestamp();
    const fileName = `test-${timestampStr}.csv`;
    const csvPath = path.join(outputDir, fileName);
    // csv出力(タブ区切り)
    const header = [
      "テスト名",
      "最終URL",
      "結果",
      "エラー詳細",
      "実行日時",
    ].join("\t");
    const rows = results.map((r) =>
      [r.testName, r.finalUrl, r.status, r.errorMessage, r.timestamp].join(
        "\t",
      ),
    );
    const content = "\ufeff" + [header, ...rows].join("\n");
    fs.writeFileSync(csvPath, content, "utf8");
    logger(logList, `\n【CSV結果出力】 ${csvPath}`);
    fs.writeFileSync(logPath, logList.join("\n"), "utf8");
  });
  // ログを出力
  const logDir = path.join(process.cwd(), "./tests/result/logs");
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  const logtimestampStr = getFormattedTimestamp();
  const logFileName = `test-${logtimestampStr}.log`;
  const logPath = path.join(logDir, logFileName);
  fs.writeFileSync(logPath, logList.join("\n"), "utf8");
});
```


- 通常の実行方法

```sh
## ワーカー数を1に設定し、順番に実施
npx playwright test tests/sample.spec.ts --workers=1 --headed --project=chromium
```

- テストケースを指定して実行

> package.json

```json
{
  "scripts": {
    "test:sample01": "cross-env TEST_FILE=./tests/case/sample01.ts npx playwright test tests/sample.spec.ts --workers=1 --headed --project=chromium",
    "test:sample02": "cross-env TEST_FILE=./tests/case/sample02.ts npx playwright test tests/sample.spec.ts --workers=1 --headed --project=chromium"
  },
}
```

```sh
## テストケースを指定して実行
npm run test:sample01
```

## csv-writer使用する場合 

```sh
# csv-writerをインストール
npm install csv-writer
```

```ts
import { createObjectCsvStringifier } from "csv-writer";

// 結果をCSV形式で出力
  test.afterAll(async () => {
    const outputDir = path.join(process.cwd(), "result");
    if (!fs.existsSync(outputDir)) {
      // 対象ディレクト作成
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const timestampStr = getFormattedTimestamp();
    const fileName = `test-${timestampStr}.csv`;
    const csvPath = path.join(outputDir, fileName);
    // csv出力
    const csvStringifier = createObjectCsvStringifier({
      header: [
        { id: "testName", title: "テスト名" },
        { id: "finalUrl", title: "最終URL" },
        { id: "status", title: "結果" },
        { id: "errorMessage", title: "エラー詳細" },
        { id: "timestamp", title: "実行日時" },
      ],
    });
    const headerString = csvStringifier.getHeaderString();
    const recordsString = csvStringifier.stringifyRecords(results);
    const csvContent = "\ufeff" + headerString + recordsString;
    fs.writeFileSync(csvPath, csvContent, "utf8");
    console.log(`\n【CSV結果出力】 ${csvPath}`);
  });
```

## 2つのフォームがある場合

```js
// 2つ目のフォームを取得
const formB = page.locator('form.my-form-class').nth(1);

// フォーム内の送信ボタンをクリックして送信する場合
await formB.getByRole('button', { name: '送信' }).click();

// または、フォーム要素自体に submit イベントを発火させる場合
await formB.evaluate((form) => form.requestSubmit());
```

## 実機モバイルの実装方法

> 必要なもの

| 項目 | 要件 |
|------|------|
| PC | Windows 11 |
| Node.js | LTS 版（v18 以上を推奨。最低 v14） |
| Playwright | `playwright` パッケージ（`_android` API を含む） |
| ADB | Android SDK Platform Tools。PATH に登録すること |
| Android 実機 | USB デバッグが有効化できる端末 |
| 端末の Chrome | **Chrome 87 以降**（または System WebView 87 以降） |
| USB ケーブル | データ通信対応のもの（充電専用ケーブルは不可） |

> Android 実機側の設定

- 開発者オプションを有効化

```sh
1. 「設定」→「デバイス情報」→「ビルド番号」を **7 回**タップ。
2. 「開発者向けオプションが有効になりました」と表示されればOK。

※メーカーによってメニュー名や場所が異なります（例: Samsung は「設定」→「デバイス情報」→「ソフトウェア情報」→「ビルド番号」）。
```

- USBデバッグとStayawakeを有効化

```sh
- **USB デバッグ**（必須）
- **スリープモードにしない（Stay awake）**（推奨）
※スクリーンショットやレンダリング系の処理は画面が起動している必要があるため、有効化すると安定します。
```

- Chrome のフラグを有効化（重要）

```sh
1. 端末の Chrome で `chrome://flags` を開く。
2. **「Enable command line on non-rooted devices」** を検索して **Enabled** に変更。
3. Chrome を再起動する。
```

> ADB確認

```sh
adb version
```

- テストスクリプトの作成

```js
const { _android: android } = require('playwright');

(async () => {
  // 接続されている Android デバイスを取得
  const [device] = await android.devices();
  console.log(`Model: ${device.model()}`);
  console.log(`Serial: ${device.serial()}`);

  // 既存の Chrome を停止してからブラウザを起動
  await device.shell('am force-stop com.android.chrome');
  const context = await device.launchBrowser();

  // 通常の Playwright と同じように操作できる
  const page = await context.newPage();
  await page.goto('https://playwright.dev/');
  console.log('Title:', await page.title());

  // スクリーンショットを保存
  await page.screenshot({ path: 'android-page.png' });

  await context.close();
  await device.close();
})();
```

```js
// テストランナーの場合
const { test, expect, _android: android } = require('@playwright/test');

test('Android 実機で Chrome を開く', async () => {
  const [device] = await android.devices();
  await device.shell('am force-stop com.android.chrome');
  const context = await device.launchBrowser();
  const page = await context.newPage();

  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);

  await context.close();
  await device.close();
});
```

- テスト実行

```sh
node android-test.js
```

> 実機ではデフォルトのタイムアウト（30 秒）で不足することがあります。必要に応じて `context.setDefaultTimeout(120000)` などで延長