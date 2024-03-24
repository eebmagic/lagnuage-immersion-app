import { Link } from "react-router-dom";

export function About() {
  const apiURL = import.meta.env.VITE_API_URL;

  console.log(`RUNING ABOUT FUNCTION`);

  console.log(`Making api call to: ${apiURL}/snippets`);

  fetch(`http://${apiURL}/snippets`)
    .then((response) => response.json())
    .then(data => {
      console.log(data);
    })
    .catch(error => {
      console.error('There was an error!', error);
    })

  return (
    <div>
      <h1>ABOUT</h1>
      <Link to="/">Home</Link>
    </div>
  )
}
