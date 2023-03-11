"use client";

import { MDXRemote, type MDXRemoteSerializeResult } from "next-mdx-remote";
import React, { HTMLProps } from 'react';

type MdxContentProps = {
  source: MDXRemoteSerializeResult;
};

/** Place your custom MDX components here */
const MdxComponents = {
  // h1 colored in yellow
  h1: (props: HTMLProps<HTMLHeadingElement>): JSX.Element => (
    <h1 style={{ color: "#FFC107" }} {...props} />
  ),
  // Card component
  Card: (props: HTMLProps<HTMLDivElement>): JSX.Element => (
    <div
      style={{
        background: "#333",
        borderRadius: "0.25rem",
        padding: "0.5rem 1rem",
      }}
      {...props}
    />
  )
};

export function MdxContent({ source }: MdxContentProps) {
  return <MDXRemote {...source} components={MdxComponents} />;
}
