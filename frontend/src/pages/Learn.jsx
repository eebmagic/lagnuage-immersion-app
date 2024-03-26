import { useEffect, useState } from "react";

import { Stack } from "../components/Stack";

export function Learn() {
  const API_URL = import.meta.env.VITE_API_URL;

  const [snippets, setSnippets] = useState([{}]);

  useEffect(() => {
    fetch(`http://${API_URL}/snippets`)
      .then((response) => response.json())
      .then(data => {
        console.log(data);
        setSnippets(data);
      })
      .catch(error => {
        console.error('There was an error!', error);
      })
  }, []);

  return (
    <div>
      <h1>Learn</h1>
      <Stack snippets={snippets} />
    </div>
  )
}
