import { Snippet } from './Snippet';

export function Stack({ snippets }) {
  return (
    <div>
      <h2>Snippets</h2>
      {snippets.map((snippet, index) => (
        <Snippet key={index} index={index} snippet={snippet} />
      ))}
    </div>
  )
}