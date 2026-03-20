import { notFound } from 'next/navigation'
import { getPayloadClient } from '@/lib/payload'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import Link from 'next/link'
import { RichText } from '@/components/parts/richText'

// propsの定義
type Props = { params: Promise<{ slug: string }> }

export async function generateStaticParams() {
  const payload = await getPayloadClient()
  const { docs } = await payload.find({
    collection: 'posts',
    where: { status: { equals: 'published' } },
    limit: 100,
  })
  return docs.map((post) => ({ slug: post.slug }))
}

export default async function BlogDetailPage({ params }: Props) {
  const payload = await getPayloadClient()

  const { docs } = await payload.find({
    collection: 'posts',
    where: {
      slug: { equals: (await params).slug },
      status: { equals: 'published' },
    },
    depth: 2,
    limit: 1,
  })

  const post = docs[0]
  if (!post) notFound()

  const author = typeof post.author === 'object' ? post.author : null
  const categories = post.categories?.filter((c) => typeof c === 'object') ?? []

  return (
    <main className="container mx-auto max-w-3xl px-4 py-12">
      {/* カテゴリ */}
      <div className="mb-4 flex flex-wrap gap-2">
        {categories.map((cat: any) => (
          <Badge key={cat.id} variant="secondary">
            {cat.name}
          </Badge>
        ))}
      </div>

      {/* タイトル */}
      <h1 className="mb-4 text-4xl font-bold tracking-tight">{post.title}</h1>

      {/* メタ情報 */}
      <div className="mb-6 flex items-center gap-4 text-sm text-muted-foreground">
        {author && <span>著者: {author.name}</span>}
        {post.publishedAt && (
          <span>
            {new Date(post.publishedAt).toLocaleDateString('ja-JP', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>
        )}
      </div>

      <Separator className="mb-8" />

      {/* 本文（リッチテキスト） */}
      {/* <article className="prose prose-slate max-w-none"> */}
        {/* Payload の RichText レンダリングは別途 RichTextComponent を実装 */}
        {/* <pre className="whitespace-pre-wrap text-sm"> */}
          {/* {JSON.stringify(post.content, null, 2)} */}
        {/* </pre> */}
      {/* </article> */}
      <article className="prose prose-slate max-w-none">
        <RichText data={post.content} />
      </article>

      <Separator className="my-8" />

      <Link href="/blog" className="text-sm text-muted-foreground hover:underline">
        ← 記事一覧に戻る
      </Link>
    </main>
  )
}