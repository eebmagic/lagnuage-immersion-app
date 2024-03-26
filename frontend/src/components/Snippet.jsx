import { Card } from 'primereact/card';
import { Accordion, AccordionTab } from 'primereact/accordion';

export function Snippet({ snippet, index }) {
  return (
    <div key={index}>
      <Card title={snippet.id}>
        <p>{snippet.text}</p>
        <Accordion>
          <AccordionTab header="Translation">
            <p>{snippet.trans}</p>
          </AccordionTab>
        </Accordion>
      </Card>
    </div>
  )
}