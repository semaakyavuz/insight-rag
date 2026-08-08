"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

interface WebGLErrorBoundaryProps {
    children: ReactNode;
    fallback: ReactNode;
}

interface WebGLErrorBoundaryState {
    hasError: boolean;
}

export class WebGLErrorBoundary extends Component<
    WebGLErrorBoundaryProps,
    WebGLErrorBoundaryState
> {
    state: WebGLErrorBoundaryState = { hasError: false };

    static getDerivedStateFromError(): WebGLErrorBoundaryState {
        return { hasError: true };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("AnimatedGradient WebGL error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return this.props.fallback;
        }
        return this.props.children;
    }
}

export function WebGLFallback({ className }: { className?: string }) {
    return (
        <div
            className={className}
            style={{
                background:
                    "linear-gradient(135deg, #0a001a 0%, #1a0b2e 50%, #f20089 100%)",
            }}
        />
    );
}
