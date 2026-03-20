import Link from 'next/link'
import { getPayloadClient } from '@/lib/payload'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Post } from '@/payload-types'

export const dynamic = 'force-dynamic'

export default async function BlogPage() {
  const payload = await getPayloadClient()

  const { docs: posts } = await payload.find({
    collection: 'posts',
    where: {
      status: { equals: 'published' },
    },
    sort: '-publishedAt',
    depth: 2,
  })

  return (
    <main className="container mx-auto max-w-5xl px-4 py-12">
      <h1 className="mb-8 text-4xl font-bold tracking-tight">ブログ</h1>

      {posts.length === 0 ? (
        <p className="text-muted-foreground">記事がまだありません。</p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map((post) => (
            <PostCard key={post.id} post={post as Post} />
          ))}
        </div>
      )}
    </main>
  )
}

function PostCard({ post }: { post: Post }) {
  const author = typeof post.author === 'object' ? post.author : null
  const categories = post.categories?.filter((c) => typeof c === 'object') ?? []

  return (
    <Card className="flex flex-col hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="mb-2 flex flex-wrap gap-1">
          {categories.map((cat: any) => (
            <Badge key={cat.id} variant="secondary">
              {cat.name}
            </Badge>
          ))}
        </div>
        <CardTitle className="text-lg leading-snug">
          <Link href={`/blog/${post.slug}`} className="hover:underline">
            {post.title}
          </Link>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1">
        {post.excerpt && (
          <p className="text-sm text-muted-foreground line-clamp-3">{post.excerpt}</p>
        )}
      </CardContent>

      <CardFooter className="text-xs text-muted-foreground flex justify-between">
        <span>{author?.name ?? '不明'}</span>
        {post.publishedAt && (
          <span>
            {new Date(post.publishedAt).toLocaleDateString('ja-JP', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>
        )}
      </CardFooter>
    </Card>
  )
}