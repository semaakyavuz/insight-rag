import { MetalButton } from "@/components/ui/metal-button";

export default function MetalButtonDemo() {
  return (
    <div className="flex h-[420px] w-full flex-wrap items-center justify-center gap-6">
      <MetalButton variant="default">Default</MetalButton>
      <MetalButton variant="primary">Primary</MetalButton>
      <MetalButton variant="success">Success</MetalButton>
      <MetalButton variant="gold">Gold</MetalButton>
    </div>
  );
}
