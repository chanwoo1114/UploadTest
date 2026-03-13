import type {MouseEvent, ReactNode} from 'react';


interface ButtonProps {
  children: ReactNode;
  onClick?: (e: MouseEvent<HTMLButtonElement>) => void;
}

export function Button({
  children,
  onClick
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  )
}