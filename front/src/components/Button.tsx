import type {MouseEvent, ReactNode} from 'react';
import styles from './Button.module.css';

interface ButtonProps {
  children: ReactNode;
  onClick?: (e: MouseEvent<HTMLButtonElement>) => void;
  disabled?: boolean;
}

export function Button({
  children,
  onClick,
  disabled = false,
}: ButtonProps) {
  return (
    <button
      className={styles.button}
      onClick={onClick}
      type="button"
      disabled={disabled}
    >
      {children}
    </button>
  )
}