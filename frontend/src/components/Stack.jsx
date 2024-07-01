import { useState } from 'react';
import Snippet from './Snippet';

export default function Stack({ snippets }) {
  const [index, setIndex] = useState(0);
  const moveIndex = (increment) => {
    setIndex(index + increment);
  };

  return (
    <div>
      <div className="card flex flex-column gap-2">
        {(snippets.length > 0) && (index < snippets.length) ? (
          <div className="flex flex-column gap-2">
            <h2>
              {index + 1}
              /
              {snippets.length}
            </h2>
            <Snippet
              key={index}
              snippet={snippets[index]}
              moveIndex={moveIndex}
            />

          </div>
        ) : (
          <div>
            <h2>Done!</h2>
            <p>Great job! You learned all the snippets!</p>
            <p>Refresh for more</p>
          </div>
        )}
      </div>
    </div>
  );
}
