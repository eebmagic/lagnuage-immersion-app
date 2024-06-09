# Language Immersion App

A web-app that provides in context examples for your target language.

Examples can be:
- Text (pdfs, etc.)
- Audio (song lyrics, podcasts)
- Video (YouTube, downloaded media, etc.)

Ingests your provided media into a vocab set and then uses spaced repetition methods to prompt you with practice examples.

## Usage

### 1. Ingestion
Import media to the `language-app/ingestion/media/` directory.
Then manually add info to the `language-app/ingestion/media/metadata.json`.

Run `language-app/ingestion/processDocs.py` to process and ingest all the docs in the `metadata.json` file.

### 2. Server
Install the requirements and run the `language-app/server/server.py` flask script.


### 3. Frontend
Build or run in dev with the npm scripts in the `language-app/frontend/` npm project:

**Build the project:**
```shell
npm run build
```

**Run the project in dev mode:**
```shell
npm run dev
```


## TODO
<a href="https://trello.com/b/A9FOIgAC/language-immersion-app" target="_blank">Trello Board</a>

