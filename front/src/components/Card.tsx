import type {LucideIcon} from 'lucide-react';
import styles from './Card.module.css'
import type {ReactNode} from "react";


interface CardProps  {
  children: ReactNode;
  title: string;
  icon?: LucideIcon;
}

export function Card({ children, title, icon: Icon, }: CardProps) {
  return (
    <div className={styles.card}>
      {title && (
        <div className={styles.title}>
          {Icon && <Icon size={20} className={styles.icon} />}
          {title}
        </div>
      )}
      {children}
    </div>
  )
}