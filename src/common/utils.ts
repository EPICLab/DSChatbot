
export function onKeyPress(func: (e: Event) => void, e: KeyboardEvent) {
  if(e.code == 'Enter') {
    func(e);
  }
}
