import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export function About() {
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
      <h1>ABOUT</h1>
      <Link to="/">Home</Link>
      {snippets.map((snippet, index) => (
        <div key={index}>
          <h2>{snippet.id}</h2>
          <p>{snippet.text}</p>
          <p>{snippet.trans}</p>
        </div>
      ))}
    </div>
  )
}
