import { Card } from 'primereact/card';
import { Accordion, AccordionTab } from 'primereact/accordion';

export function Snippet({ snippet, index }) {
  const mediaTitle = snippet.source_path.split('/').pop().split('.')[0];
  const subTitle = `page ${snippet.page} : sentence ${snippet.page_sentence_index}`;

  return (
    <div key={index}>
      <Card title={mediaTitle} subTitle={subTitle}>
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