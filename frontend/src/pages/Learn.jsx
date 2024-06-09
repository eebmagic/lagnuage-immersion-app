import { useEffect, useState } from "react";

import { Stack } from "../components/Stack";

const API_URL = import.meta.env.VITE_API_URL;
const GET_SNIPPETS_API_PATH = `http://${API_URL}/snippets?N=3`;

export function Learn() {

  const [snippets, setSnippets] = useState([{}]);
  const [vocab, setVocab] = useState([{}]);

  useEffect(() => {
    fetch(GET_SNIPPETS_API_PATH)
      .then((response) => response.json())
      .then(data => {
        console.log(data);
        setSnippets(data.snippets);
        setVocab(data.vocab);
        console.log(`SET VOCAB:`);
        console.log(data.vocab)
      })
      .catch(error => {
        console.error('There was an error!', error);
      })
  }, []);

  return (
    <div>
      <h1>Learn</h1>
      <p>{vocab.map(x => x.lemma)}</p>
      <Stack snippets={snippets} />
    </div>
  )
}
