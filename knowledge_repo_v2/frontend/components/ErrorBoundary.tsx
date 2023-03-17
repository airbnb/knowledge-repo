'use client' // this is a client component

import React, { Component } from 'react'

class ErrorBoundary extends Component<any, { hasError: boolean }> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() {
    return { hasError: true }
  }
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.log({ error, errorInfo })
  }
  render() {
    if (this.state?.hasError) {
      return <div>Oops, there&apos;s an error</div>
    }
    return this.props.children
  }
}

export default ErrorBoundary
