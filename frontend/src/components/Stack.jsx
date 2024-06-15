import { Snippet } from './Snippet';
import { useState } from 'react';
import { Button } from 'primereact/button';

import { useUser } from "../UserContext.jsx";

const API_URL = import.meta.env.VITE_API_URL;
const POST_REP_API_PATH = `http://${API_URL}/rep`;

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
  const { user } = useUser();

  const logButtonFunc = (snippet, label, username) => {
    const payload = {
      strength: label.toLowerCase(),
      review_time: Date.now() / 1000,
      vocab: snippet.contained_vocab,
    }

    // post the payload to to 
    const fullUrl = `${POST_REP_API_PATH}?username=${username}`
    fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        if (response.status == 200) {
          // Increment the index if a good response comes back
          setIndex(index + 1);
        } else {
          console.log(`Got back this response: ${response.status}`);
          console.log(response);
          response.json().then(data => {
            console.log(`Got back this response data as json:`);
            console.log(data);
          })
        }
      })
      .catch((error) => {
        console.error('There was a problem with your fetch operation:', error);
      })
  };

  return (
    <div>
      <h2>Learn this snippet</h2>
      <div className="card flex flex-column gap-2">
        { (snippets.length > 0) && (index < snippets.length) ? (
            <div className="flex flex-column gap-2">
              <h2>{index+1} / {snippets.length}</h2>
              <Snippet snippet={snippets[index]} index={index} />

              <div className="card flex flex-wrap justify-content-center gap-3">
                {buttonOptions.map(({ label, severity }) => (
                  <Button
                    key={label}
                    label={label}
                    severity={severity}
                    onClick={() => logButtonFunc(snippets[index], label, user.username)}
                  />
                ))}
              </div>
              <div className='card flex flex-wrap justify-content-center gap-3'>
                <Button label='Again' severity='danger' />
                <Button label='Hard' severity='warning' />
                <Button label='Good' style={{ backgroundColor: '#8c9234', borderColor: '#8c9234', color: 'white' }} />
                <Button label='Easy' severity='success' />
              </div>
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