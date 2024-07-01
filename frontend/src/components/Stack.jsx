import { Snippet } from './Snippet';
import { useState } from 'react';

export function Stack({ snippets }) {
  const [index, setIndex] = useState(0);
  const moveIndex = (increment) => {
    setIndex(index + increment);
  };

  return (
    <div>
      <h2>Learn this snippet</h2>
      <div className="card flex flex-column gap-2">
        { (snippets.length > 0) && (index < snippets.length) ? (
            <div className="flex flex-column gap-2">
              <h2>{index+1} / {snippets.length}</h2>
              <Snippet
                key={index}
                snippet={snippets[index]}
                moveIndex={moveIndex}
              />

            </div>
          ) : (
            <div>
              <h2>Done!</h2>
              <p>Great job! You've learned all the snippets!</p>
              <p>Refresh for more</p>
            </div>
          )
        }
      </div>
    </div>
  )
}