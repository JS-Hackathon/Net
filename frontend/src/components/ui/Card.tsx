import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  headerActions?: React.ReactNode;
  footer?: React.ReactNode;
  padding?: "none" | "sm" | "md" | "lg";
  shadow?: "none" | "sm" | "md" | "lg";
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      title,
      subtitle,
      headerActions,
      footer,
      padding = "md",
      shadow = "sm",
      children,
      ...props
    },
    ref
  ) => {
    const paddings = {
      none: "p-0",
      sm: "p-4",
      md: "p-6",
      lg: "p-8",
    };

    const shadows = {
      none: "shadow-none",
      sm: "shadow-sm border border-border",
      md: "shadow-md border border-border/80",
      lg: "shadow-lg border border-border/60",
    };

    return (
      <div
        ref={ref}
        className={cn(
          "rounded-xl bg-card text-card-foreground",
          shadows[shadow],
          className
        )}
        {...props}
      >
        {/* Header */}
        {(title || subtitle || headerActions) && (
          <div className="flex items-start justify-between border-b border-border/50 px-6 py-4">
            <div className="flex flex-col gap-1">
              {title && <h3 className="text-lg font-semibold leading-none tracking-tight">{title}</h3>}
              {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
            </div>
            {headerActions && <div className="flex items-center">{headerActions}</div>}
          </div>
        )}

        {/* Content */}
        <div className={paddings[padding]}>{children}</div>

        {/* Footer */}
        {footer && (
          <div className="flex items-center justify-end border-t border-border/50 px-6 py-4">
            {footer}
          </div>
        )}
      </div>
    );
  }
);

Card.displayName = "Card";
export default Card;
