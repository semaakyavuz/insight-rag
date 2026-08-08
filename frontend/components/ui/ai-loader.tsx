import { cn } from "@/lib/utils";

interface ComponentProps {
  className?: string;
}

export const Component = ({ className }: ComponentProps) => {
  return (
    <div className={cn("loader-wrapper", className)}>
      <span className="loader-letter">G</span>
      <span className="loader-letter">e</span>
      <span className="loader-letter">n</span>
      <span className="loader-letter">e</span>
      <span className="loader-letter">r</span>
      <span className="loader-letter">a</span>
      <span className="loader-letter">t</span>
      <span className="loader-letter">i</span>
      <span className="loader-letter">n</span>
      <span className="loader-letter">g</span>

      <div className="loader" />
    </div>
  );
};
