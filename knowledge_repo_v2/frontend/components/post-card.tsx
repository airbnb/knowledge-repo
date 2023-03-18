'use client';

import Link from 'next/link';
import { type Post } from 'contentlayer/generated';
import { Calendar } from 'lucide-react';
import Balancer from 'react-wrap-balancer';

import { PostTags } from '@/components/post-tags';
import { formatDateTime } from '@/lib/datetime';
import { cn } from '@/lib/utils';

type PostCardProps = {
  post: Post;
};

export function PostCard({ post }: PostCardProps) {
  const publishedDate = formatDateTime(post.date);

  return (
    <Link
      href={post.url}
      className={cn(
        'group relative flex h-fit w-full',
        'transition-transform duration-300 ease-in-out hover:scale-[1.02]',
      )}
      aria-label={post.title}
    >
      <article
        className={cn(
          'flex h-fit w-full flex-col space-y-4 rounded',
          'relative z-10 m-0.5 py-3 pl-10 pr-6 shadow-lg hover:shadow-xl',
          'bg-slate-100/95 dark:bg-slate-600/90',
        )}
      >
        <div className="flex flex-col space-y-2">
          <h2 className="text-2xl font-bold leading-normal text-slate-800 dark:text-rose-50 sm:text-3xl">
            <Balancer>
              {post.title}
              {publishedDate.isFresh && (
                <>
                  {' '}
                  <sup className="text-base font-semibold text-accent dark:text-accent-dark">
                    New
                  </sup>
                </>
              )}
            </Balancer>
          </h2>
          <p className="text-slate-700 dark:text-rose-50">
            <Balancer>{post.excerpt}</Balancer>
          </p>
          <p className="inline-flex items-center space-x-1 text-slate-600/90 dark:text-rose-50/80">
            <Calendar className="h-4 w-4 self-baseline" aria-hidden />
            <span className="text-sm">
              Published {publishedDate.asString}{' '}
              <span className="opacity-95 max-xs:hidden">
                · {publishedDate.asRelativeTimeString}
              </span>
            </span>
          </p>
        </div>
        <PostTags tags={post.tags} className="text-sm sm:text-xs" />
      </article>
      <div
        className={cn(
          'absolute inset-0 z-20 my-auto h-[calc(100%_-_0.25rem)] w-4 rounded-l',
          'group-hover:animate-border group-focus:animate-border-fast',
          'bg-slate-700 dark:bg-rose-50',
        )}
      />
    </Link>
  );
}