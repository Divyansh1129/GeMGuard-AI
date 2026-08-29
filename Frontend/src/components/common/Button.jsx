import React from "react";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  className = "",
  disabled = false,
  onClick,
  type = "button",
  ...props
}) {
  const baseStyles =
    "inline-flex items-center justify-center font-medium transition-all duration-200 rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
    lg: "px-6 py-3 text-base gap-2.5",
  };

  const variantStyles = {
    primary:
      "bg-primary text-on-primary hover:bg-primary-container focus:ring-primary shadow-sm",
    secondary:
      "bg-surface-container-lowest border border-outline-variant text-on-surface hover:bg-surface-container-high focus:ring-primary",
    outline:
      "bg-transparent border border-outline text-on-surface hover:bg-surface-container-high focus:ring-primary",
    danger:
      "bg-error text-on-error hover:bg-error/90 focus:ring-error shadow-sm",
    ghost:
      "bg-transparent text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface",
    success:
      "bg-success text-white hover:bg-success/90 focus:ring-success shadow-sm",
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${baseStyles} ${sizeStyles[size] || sizeStyles.md} ${
        variantStyles[variant] || variantStyles.primary
      } ${className}`}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4 shrink-0" />}
      {children}
    </button>
  );
}
