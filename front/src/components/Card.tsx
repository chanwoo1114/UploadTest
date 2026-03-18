import type {LucideIcon} from 'lucide-react';
import styles from './Card.module.css'
import type {ReactNode} from "react";


interface CardProps  {
  children: ReactNode;
  title: string;
  icon?: LucideIcon;
  variant?: 'default' | 'chart' | 'summary';
}

const CARD_CLASS = {
  default: styles.card,
  summary: styles.summaryCard
}

const TITLE_CLASS = {
  default: styles.title,
  summary: ''
}

export function Card({ children, title, icon: Icon, variant = "default"}: CardProps) {
  const cardClass = CARD_CLASS[variant];
  const titleClass = TITLE_CLASS[variant];

  return (
    <div className={cardClass}>
      {title && (
        <div className={titleClass}>
          {Icon && <Icon size={20} className={styles.icon} />}
          {title}
        </div>
      )}
      {children}
    </div>
  )
}