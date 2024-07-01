import { useEffect, useState } from "react";
import { Button } from 'primereact/button';

import Stack from "../components/Stack";

const API_URL = import.meta.env.VITE_API_URL;
const GET_SNIPPETS_API_PATH = `http://${API_URL}/snippets?N=3`;

export function Learn() {
  const [snippets, setSnippets] = useState([]);
  const [vocab, setVocab] = useState([]);

  const updateFunc = () => {
    console.log(`Making call to api path: ${GET_SNIPPETS_API_PATH}`);
    fetch(GET_SNIPPETS_API_PATH)
      .then((response) => response.json())
      .then(data => {
        console.log('Api call got response data:', data);
        setSnippets(data.snippets);
        setVocab(data.vocab);
        console.log('SET VOCAB:', data.vocab);
      })
      .catch(error => {
        console.error('There was an error!', error);
      })
  };

  useEffect(() => {
    if (snippets.length === 0) {
      updateFunc();
    }
  }, [snippets])

  return (
    <div>
      <h1>Learn</h1>
      <Button
        label='REFRESH'
        onClick={updateFunc}
        severity='success'
        icon='pi pi-refresh'
      />
      {
        (snippets.length > 0) ? (
          <div>
            <div className="flex flex-grid justify-content-center">
              <h2> Learning these vocab items: </h2>
              <div clasName="flex flex-grid justify-content-left" style={{ listStylePosition: 'outside', textAlign: 'left'}}>
                <ul>
                  {vocab.map((x) => <li key={x.lemma}>{x.lemma}</li>)}
                </ul>
              </div>
            </div>
            <Stack snippets={snippets} />
          </div>
        ) : (
          <p>please hit the refresh button</p>
        )
      }
    </div>
  )
}
