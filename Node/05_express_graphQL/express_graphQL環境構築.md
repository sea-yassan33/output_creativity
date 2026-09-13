# Express + GraphQL 環境構築

## 1.インストール

```sh

npm init -y
mkdir src

## 本番用の依存パッケージ
npm install express express-graphql graphql

## typescript導入
npm install --save-dev typescript@^5.9.0 ts-node ts-node-dev @types/node @types/express

```

| パッケージ | 役割 |
|---|---|
| `express` | Node.js用Webフレームワーク |
| `graphql` | GraphQLの仕様を実装したコアライブラリ |
| `express-graphql` | ExpressにGraphQLエンドポイントを組み込むミドルウェア（型定義を内包しているため`@types/express-graphql`は不要） |
| `typescript` | TypeScriptコンパイラ |
| `ts-node` | TypeScriptをコンパイルせず直接実行 |
| `ts-node-dev` | ファイル変更を検知して自動再起動する開発サーバー |
| `@types/node`, `@types/express` | Node.js / Expressの型定義 |


## 2.tsconfig.jsonの作成

```sh
npx tsc --init
```

> tsconfig.jsonの作成

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

> package.jsonにスクリプトを追加

```json
"scripts": {
  "dev": "ts-node-dev --respawn --transpile-only src/server.ts",
  "build": "tsc",
  "start": "node dist/server.js"
}
```

| コマンド | 役割 |
|---|---|
| `npm run dev` | ソース変更を検知して自動再起動する開発モード |
| `npm run build` | `dist/` にJSへコンパイル |
| `npm start` | コンパイル済みのJSを実行 |

## 3.ディレクトリ構成

```sh
project/
├── package.json
├── tsconfig.json
├── src/
│   ├── lib/common.ts # 型定義
│   ├── data/data.ts  # サンプルデータ（著者・書籍）
│   ├── schema.ts     # GraphQLスキーマ（Query・Mutation）
│   └── server.ts     # Expressサーバー本体
└── README.md
```

## 4.実装

> 型定義

- project\src\data\data.ts

```ts
// interface
export interface Author {
  id: string;
  name: string;
  birthYear: number;
}
export interface Book {
  id: string;
  title: string;
  authorId: string;
  publishedYear: number;
}

export interface IdArgs {
  id: string;
}

```

> サンプルデータ（著者・書籍）

```ts
import { Author, Book } from "../lib/common";
// data
export const authors: Author[] = [
  { id: "1", name: "夏目漱石", birthYear: 1867 },
  { id: "2", name: "芥川龍之介", birthYear: 1892 },
  { id: "3", name: "太宰治", birthYear: 1909 },
];
export const books: Book[] = [
  { id: "1", title: "吾輩は猫である", authorId: "1", publishedYear: 1905 },
  { id: "2", title: "こころ", authorId: "1", publishedYear: 1914 },
  { id: "3", title: "羅生門", authorId: "2", publishedYear: 1915 },
  { id: "4", title: "人間失格", authorId: "3", publishedYear: 1948 },
  { id: "5", title: "走れメロス", authorId: "3", publishedYear: 1940 },
];
```

> GraphQLスキーマ（Query・Mutation）

- project\src\schema.ts

```ts
import {
  GraphQLObjectType,
  GraphQLSchema,
  GraphQLString,
  GraphQLInt,
  GraphQLList,
  GraphQLNonNull,
  GraphQLID,
} from "graphql";

import { Author, Book, IdArgs } from "./lib/common";
import { authors, books } from "./data/data";

// Author型定義
const AuthorType: GraphQLObjectType = new GraphQLObjectType({
  name: "Author",
  fields: () => ({
    id: { type: new GraphQLNonNull(GraphQLID) },
    name: { type: new GraphQLNonNull(GraphQLString) },
    birthYear: { type: GraphQLInt },
    // リレーション
    books: {
      type: new GraphQLList(BookType),
      resolve: (author: Author): Book[] =>
        books.filter((book) => book.authorId === author.id),
    },
  }),
});

// Book型定義
const BookType: GraphQLObjectType = new GraphQLObjectType({
  name: "Book",
  fields: () => ({
    id: { type: new GraphQLNonNull(GraphQLID) },
    title: { type: new GraphQLNonNull(GraphQLString) },
    publishedYear: { type: GraphQLInt },
    // リレーション
    authorId: { type: new GraphQLNonNull(GraphQLID) },
    author: {
      type: AuthorType,
      resolve: (book: Book): Author | undefined =>
        authors.find((author) => author.id === book.authorId),
    },
  }),
});

// Query:データの取得
const RootQueryType = new GraphQLObjectType({
  name: "Query",
  fields: () => ({
    books: {
      type: new GraphQLList(BookType),
      resolve: (): Book[] => books,
    },
    book: {
      type: BookType,
      args: { id: { type: new GraphQLNonNull(GraphQLID) } },
      resolve: (_parent: unknown, args: any): Book | undefined => {
        const { id } = args as IdArgs;
        return books.find((book) => book.id === id);
      },
    },
    authors: {
      type: new GraphQLList(AuthorType),
      resolve: (): Author[] => authors,
    },
    author: {
      type: AuthorType,
      args: { id: { type: new GraphQLNonNull(GraphQLID) } },
      resolve: (_parent: unknown, args: any): Author | undefined => {
        const { id } = args as IdArgs;
        return authors.find((author) => author.id === id);
      },
    },
  }),
});

// Mutation: データ作成・更新・削除の処理
const RootMutationType = new GraphQLObjectType({
  name: "Mutation",
  fields: () => ({
    // 新しい本を追加
    addBook: {
      type: BookType,
      args: {
        // GraphQLNonNullは必須
        title: { type: GraphQLNonNull(GraphQLString) },
        authorId: { type: GraphQLNonNull(GraphQLID) },
        publishedYear: { type: GraphQLInt },
      },
      // 実行処理
      resolve: (parent, args) => {
        const newBook = {
          // 新規ID（配列長+1）を発行
          id: String(books.length + 1),
          title: args.title,
          authorId: args.authorId,
          publishedYear: args.publishedYear,
        };
        books.push(newBook);
        return newBook;
      },
    },
    addAuthor: {
      type: AuthorType,
      args: {
        name: { type: GraphQLNonNull(GraphQLString) },
        birthYear: { type: GraphQLInt },
      },
      resolve: (parent, args) => {
        const newAuthor = {
          id: String(authors.length + 1),
          name: args.name,
          birthYear: args.birthYear,
        };
        authors.push(newAuthor);
        return newAuthor;
      },
    },
    // 本を削除
    deleteBook: {
      type: BookType,
      args: { id: { type: GraphQLNonNull(GraphQLID) } },
      resolve: (parent, args) => {
        const index = books.findIndex((book) => book.id === args.id);
        if (index === -1) return null;
        const [deleted] = books.splice(index, 1);
        return deleted;
      },
    },
  }),
});

// スキーマオブジェクトにまとめる
const schema = new GraphQLSchema({
  query: RootQueryType,
  mutation: RootMutationType,
});
export default schema;

```

> Expressサーバー本体

```ts
import express, { Request, Response } from "express";
import { graphqlHTTP } from "express-graphql";
import schema from "./schema";

const app = express();
const PORT = process.env.PORT || 4000;

app.use(
  "/graphql",
  graphqlHTTP({
    schema,
    graphiql: true, // ブラウザからGraphiQLを使えるようにする
  }),
);

app.get("/", (_req: Request, res: Response) => {
  res.send("GraphQL server is running. Access /graphql to use the API.");
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/graphql`);
});

```

## 5.起動方法

> 開発時（ホットリロードあり）

```sh
npm run dev
```

> 本番相当（ビルドしてから実行）

```sh
# dist/ にコンパイル
npm run build
# dist/server.js を実行
npm start
```

> ブラウザで以下にアクセスし、GraphiQL画面を開く

http://localhost:4000/graphql

## 6.GraphiQL画面でのクエリ方法

> 書籍一覧の取得

```json
{
  books {
    id
    title
    publishedYear
    author {
      name
    }
  }
}
```

> 特定の著者とその著作一覧を取得

```json
{
  author(id: "3") {
    name
    books {
      title
      publishedYear
    }
  }
}
```

> Mutation：著者の追加

```json
mutation {
  addAuthor(name: "森鴎外", birthYear: 1862) {
    id
    name
    birthYear
  }
}
```

## 7.curlでの動作確認

```sh
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ books { id title author { name } } }"}'
```