import { AnimatedGradient } from "@/components/ui/animated-gradient";

export default function AnimatedGradientDemo() {
  return (
    <div className="relative h-[420px] w-full max-w-2xl overflow-hidden rounded-xl">
      <AnimatedGradient config={{ preset: "Aurora" }} radius="12px" />
      <div className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center">
        <h1 className="text-5xl font-semibold leading-tight tracking-tight text-white">
          Animated
          <br />
          Gradient
        </h1>
      </div>
    </div>
  );
}
