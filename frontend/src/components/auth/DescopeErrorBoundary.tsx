"use client";

import React from "react";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
}

export class DescopeErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.warn("Descope provider failed, running without auth SDK:", error.message);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? this.props.children;
    }
    return this.props.children;
  }
}
