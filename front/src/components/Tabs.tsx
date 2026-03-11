import type {TabItem} from '../types';
import styles from './Tabs.module.css'

interface TabsProps {
  tabs: TabItem[];
}

export function Tabs({ tabs, }: TabsProps) {
  return (
    <div className={styles.tabs}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={styles.tab}
        >
          {tab.icon && <span className={styles.icon}>{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
  );
}