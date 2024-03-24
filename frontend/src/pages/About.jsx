import { Link } from "react-router-dom";

export function About() {
    console.log(`RUNING ABOUT FUNCTION`);
    return (
        <div>
          <h1>ABOUT</h1>
          <Link to="/">Home</Link>
        </div>
    )
}
