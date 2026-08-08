"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { AnimatedGradient } from "@/components/ui/animated-gradient";
import { MetalButton } from "@/components/ui/metal-button";

interface HeroParallaxProps {
  onCtaClick?: () => void;
}

export function HeroParallax({ onCtaClick }: HeroParallaxProps) {
  const container = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: container,
    offset: ["start end", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "10%"]);

  return (
    <div
      ref={container}
      className="relative flex h-[60vh] min-h-95 w-full items-center justify-center overflow-hidden sm:h-[70vh]"
    >
      <motion.div
        className="absolute inset-x-0 -top-[10%] h-[120%] w-full"
        style={{ y }}
      >
        <AnimatedGradient config={{ preset: "Aurora" }} />
      </motion.div>

      <div className="relative z-10 flex flex-col items-center gap-3 px-6 text-center sm:gap-6">
        <h1 className="font-heading text-4xl font-bold tracking-tight text-white sm:text-6xl">
          InsightRAG
        </h1>
        <p className="max-w-md text-sm text-white/80 sm:text-lg">
          Dokümanlarınla konuş, anında cevap al
        </p>
        <MetalButton
          variant="primary"
          onClick={onCtaClick}
          className="mt-2 h-9 px-4 text-xs sm:h-11 sm:px-6 sm:text-sm"
        >
          Başla
        </MetalButton>
      </div>
    </div>
  );
}
