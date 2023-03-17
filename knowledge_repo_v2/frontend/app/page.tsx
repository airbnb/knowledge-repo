import { type MDXRemoteSerializeResult } from "next-mdx-remote";
import { serialize } from "next-mdx-remote/serialize";
import { promises as fs } from "fs";
import { MdxContent } from "../components/mdx-content";
import type { AppProps } from 'next/app';
import ErrorBoundary from "../components/ErrorBoundary";


type Frontmatter = {
  title: string;
  created_at: string;
};

type Post<TFrontmatter> = {
  serialized: MDXRemoteSerializeResult;
  frontmatter: TFrontmatter;
};

async function getPost(filepath: string): Promise<Post<Frontmatter>> {
  // Read the file from the filesystem
  const raw = await fs.readFile(filepath, "utf-8");

  // Serialize the MDX content and parse the frontmatter
  const serialized = await serialize(raw, {
    parseFrontmatter: true,
  });

  // Typecast the frontmatter to the correct type
  const frontmatter = serialized.frontmatter as Frontmatter;

  // Return the serialized content and frontmatter
  return {
    frontmatter,
    serialized,
  };
}



export default async function Home(props: AppProps) {
  const { Component, pageProps } = props;

  const { serialized, frontmatter } = await getPost("content/test_post.mdx");

  return (
    <ErrorBoundary>
      <div style={{ maxWidth: 600, margin: "auto" }}>
        <h1>{frontmatter.title}</h1>
        <p>Published {frontmatter.created_at}</p>
        <hr />
        <MdxContent source={serialized} />
      </div>
    </ErrorBoundary>
  );
}
