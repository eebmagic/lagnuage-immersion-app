import { useState } from 'react';
import { Card } from 'primereact/card';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Button } from 'primereact/button';

import DiffGrid from './DiffGrid';
import { useUser } from '../UserContext';
import buttonOptions from './ButtonOptions';

const API_URL = import.meta.env.VITE_API_URL;
const POST_REP_API_PATH = `http://${API_URL}/rep`;

export default function Snippet({
  snippet,
  moveIndex,
}) {
  const mediaTitle = snippet.source_path.split('/').pop().split('.')[0];
  const subTitle = `page ${snippet.page} : sentence ${snippet.page_sentence_index}`;

  const { user } = useUser();
  const { username } = user;
  const updateFunc = (vocabList, difficulty, shouldIncrement) => {
    const payload = {
      strength: difficulty.toLowerCase(),
      review_time: Date.now() / 1000,
      vocab: vocabList,
    };

    const fullUrl = `${POST_REP_API_PATH}?username=${username}`;
    fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        if (response.headers.get('Content-Type') !== 'application/json') {
          throw new Error('Content-Type is not application/json');
        }

        let all200 = false;
        let data = null;
        if (response.status === 207) {
          data = await response.json();
          all200 = data.codes
            ? data.codes.every((code) => (code >= 200) && (code < 300))
            : false;
        }

        if (response.status === 200 || response.status === 204 || all200) {
          // Increment the index if a good response comes back
          if (shouldIncrement) {
            moveIndex(1);
          }
        } else {
          console.log(`Got back this response: ${response.status}`);
          console.log(response);
          if (!data) {
            data = await response.json();
          }
          console.log('data', data);
        }
      })
      .catch((error) => {
        console.error(payload, 'There was a problem with your fetch operation:', error);
      });
  };

  const [accordionIndex, setAccordionIndex] = useState([]);

  return (
    <div key={snippet.id}>
      <Card title={mediaTitle} subTitle={subTitle}>
        <div className="card flex flex-column gap-0">
          <p>{snippet.text}</p>
          <Accordion
            multiple
            activeIndex={accordionIndex}
            onTabChange={(e) => setAccordionIndex(e.index)}
          >
            <AccordionTab header="Translation">
              <p>{snippet.translation}</p>
            </AccordionTab>
            <AccordionTab header="Specific Word Difficulty">
              <DiffGrid
                snippet={snippet}
                updateFunc={updateFunc}
              />
            </AccordionTab>
          </Accordion>

          {/* Buttons to increment */}
          <div className="card flex flex-column gap-3">
            <div className="flex flex-wrap justify-content-center gap-3">
              {Object.values(buttonOptions).map(({ difficulty, severity, color }) => (
                <Button
                  key={difficulty}
                  label={difficulty}
                  severity={severity}
                  disabled={accordionIndex.includes(1)}
                  style={color ? { backgroundColor: color, borderColor: color, color: 'white' } : {}}
                  onClick={() => updateFunc(snippet.contained_vocab, difficulty, true)}
                />
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
