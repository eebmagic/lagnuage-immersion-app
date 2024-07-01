import { useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Checkbox } from 'primereact/checkbox';
import { Button } from 'primereact/button';

import buttonOptions from './ButtonOptions';

export default function DiffGrid({ snippet, updateFunc }) {
  const difficulties = ['Easy', 'Good', 'Hard', 'Again'];

  const startingState = snippet.texts.map((item) => ({
    Easy: false,
    Good: false,
    Hard: false,
    Again: false,
    vocab: item.vocab,
  }));
  const [checkedState, setCheckedState] = useState(startingState);

  const toggleRow = (difficulty) => {
    const newCheckedState = checkedState.map(() => ({
      Easy: difficulty === 'Easy',
      Good: difficulty === 'Good',
      Hard: difficulty === 'Hard',
      Again: difficulty === 'Again',
    }));
    setCheckedState(newCheckedState);
  };

  const handleCheckboxChange = (wordIndex, difficulty) => {
    const newCheckedState = [...checkedState];
    newCheckedState[wordIndex] = {
      Easy: difficulty === 'Easy',
      Good: difficulty === 'Good',
      Hard: difficulty === 'Hard',
      Again: difficulty === 'Again',
    };
    setCheckedState(newCheckedState);
  };

  const createRowData = () => difficulties.map((difficulty, diffIndex) => {
    const options = buttonOptions[difficulty];
    const rowData = {
      toggle: (
        <Button
          key={`button: ${difficulty}`}
          label={difficulty}
          severity={options.severity}
          style={options.color ? { backgroundColor: options.color, borderColor: options.color, color: 'white' } : {}}
          onClick={() => toggleRow(difficulty, !checkedState[diffIndex][difficulty])}
        />
      ),
    };
    snippet.texts.forEach((word, wordIndex) => {
      rowData[word.text] = (
        <Checkbox
          inputId={`${word.text}-${difficulty}`}
          checked={checkedState[wordIndex][difficulty]}
          onChange={() => handleCheckboxChange(wordIndex, difficulty)}
          key={`${word.text}-${difficulty}`}
        />
      );
    });
    return rowData;
  });

  const truncate = (text, length) => {
    if (text.length > length) {
      return `${text.substring(0, length)}..`;
    }
    return `${text}${' '.repeat(length - text.length)}`;
  };

  const columns = [
    { field: 'toggle', header: 'Set Row', id: 'buttons' },
    ...snippet.texts.map((word, i) => ({
      field: word.text,
      header: truncate(word.text, 4),
      id: i,
    })),
  ];

  const sendUpdates = () => {
    const groupings = {};
    snippet.texts.forEach((item, itemIndex) => {
      const attribute = Object.keys(checkedState[itemIndex])
        .filter((key) => checkedState[itemIndex][key] === true)[0];
      if (attribute === undefined) {
        return;
      }
      if (groupings[attribute]) {
        groupings[attribute].add(item.vocab);
      } else {
        groupings[attribute] = new Set([item.vocab]);
      }
    });

    Object.keys(groupings).forEach((difficulty, index) => {
      const vocabList = Array.from(groupings[difficulty]);
      const isLast = index === Object.keys(groupings).length - 1;

      updateFunc(vocabList, difficulty, isLast);
    });
  };

  return (
    <div className="flex flex-column gap-2">
      <div>
        <Button
          label="Next"
          icon="pi pi-arrow-right"
          iconPos="right"
          severity="info"
          onClick={sendUpdates}
        />
      </div>
      <DataTable
        value={createRowData()}
        className="p-datatable-gridlines"
        tooltip="Word Difficulty"
      >
        {columns.map((col) => (
          <Column key={col.id} field={col.field} header={col.header} />
        ))}
      </DataTable>
    </div>
  );
}
