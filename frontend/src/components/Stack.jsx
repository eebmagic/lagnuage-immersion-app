import { Snippet } from './Snippet';
import { useState } from 'react';
import { Button } from 'primereact/button';

// import "primereact/resources/themes/lara-dark-blue/theme.css";
// import "primeicons/primeicons.css";

const buttonOptions = [
  {
    label: 'Again',
    severity: 'danger',
  },
  {
    label: 'Hard',
    severity: 'warning',
  },
  {
    label: 'Good',
    severity: 'info',
  },
  {
    label: 'Easy',
    severity: 'success',
  }
];

export function Stack({ snippets }) {
  const [index, setIndex] = useState(0);

  return (
    <div>
      <h2>Learn this snippet</h2>
      {/* {snippets.map((snippet, index) => (
        <Snippet key={index} index={index} snippet={snippet} />
      ))} */}

      <Snippet snippet={snippets[index]} index={index} />

      <div className="card flex flex-wrap justify-content-center gap-3">
        {buttonOptions.map(({ label, severity }) => (
          <Button
            key={label}
            label={label}
            severity={severity}
            // severity="danger"
            onClick={() => {console.log(`clicked on button for: ${label}`)}}
          />
        ))}
      </div>
    </div>
  )
}