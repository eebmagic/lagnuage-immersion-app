import { Card } from 'primereact/card';
import { Accordion, AccordionTab } from 'primereact/accordion';

// import "primereact/resources/themes/lara-dark-blue/theme.css";
// import "primeicons/primeicons.css";

export function Snippet({ snippet, index }) {
  return (
    <div key={index}>
      <Card title={snippet.id}>
        <p>{snippet.text}</p>
        <Accordion>
          <AccordionTab header="Translation">
            <p>{snippet.translation}</p>
          </AccordionTab>
        </Accordion>
      </Card>
    </div>
  )
}