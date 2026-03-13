import {METHODS} from "../utils";
import type {UploadMethod} from '../types';
import styles from './MethodSelector.module.css'

interface MethodSelectorProps {
  selected: UploadMethod;
  onChange: (method: UploadMethod) => void;
}

export function MethodSelector({ selected, onChange }: MethodSelectorProps) {
  const methodEntries = Object.entries(METHODS) as [UploadMethod, typeof METHODS[UploadMethod]][];

  return (
    <div className={styles.grid}>
      {methodEntries.map(([key, method]) => (
        <button
         key={key}
         type="button"
         className={`${styles.btn} ${selected === key ? styles.selected : ''}`}
         onClick={() => onChange(key)}
        >
          <div className={styles.name}>
            {method.name}
            <span
              className={styles.badge}
              style={{background: `${method.color}20`, color:method.color}}
            >
              {method.badge}
            </span>
          </div>
          <div className={styles.desc}>
            {method.desc}
          </div>

        </button>
      ))}
    </div>
  );
}