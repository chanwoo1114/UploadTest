import type {UploadMethod} from '../types';

interface MethodSelectorProps {
  selected: UploadMethod;
  onChange: (method: UploadMethod) => void;
}

// export function MethodSelector({ selected, onChange }: MethodSelectorProps) {
//   const methodEntries = Object.entries(METHODS) as [UploadMethod, typeof METHODS[UploadMethod]][];
//
//   return (
//     <></>
//   )
// }