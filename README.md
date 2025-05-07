# Fresh install instructions

Clone the repository:
```bash
git clone https://github.com/kulpsin/healthAssistant

```
Clone the [pgvector](https://github.com/pgvector/pgvector) repository:
```bash
cd healthAssistant/database
clone https://github.com/pgvector/pgvector.git
cd ..
```
Modify the environment variables, build and start containers.
```bash
cp .env.template .env
# Edit .env file
docker compose up -d --build
```

Browse to [localhost:3000](http://localhost:3000/) and create an admin account.

# Ollama models

You can follow [these instructions](https://github.com/ollama/ollama/blob/main/docs/import.md) to import a model (which you have downloaded before) into ollama. Note that instead of `ollama create my-model`, you need to run the command in container: `docker exec -it ollama ollama create my-model`.

You can also browse [Ollama library](https://ollama.com/library) for their hosted models and install them with ollama run command.

# Add FHIR data to database

You can use for example the following curl command to insert a FHIR-json into database:

```bash
curl localhost:8000/reindex\
  -d @path/to/json/0006a28d-fb47-40cf-afa8-32360c384798.json\
  -H 'Content-Type: application/json' 
```

Note that FHIR JSON format is not fully supported yet, only following files have been tested to work:
- `0006a28d-fb47-40cf-afa8-32360c384798.json`
- `000b837b-1ee8-4eb1-aea6-0469f1128e43.json`
- `000dc563-9b0a-4890-9c09-a61314ba9e5c.json`
- `000fe04a-7a4e-43cf-95f6-feaa1ffa9fb1.json`
- `0124a570-1e58-4217-b515-b4ef8917744f.json`

These are part of synthea dataset which can be downloaded from [kaggle](https://www.kaggle.com/datasets/krsna540/synthea-dataset-jsons-ehr).

# OpenWebUI

## Knowledge - Clinical Guidelines

Before inserting any documents to the knowledge, the embedding model settings 
must be modified unless opting for the default: all the documents must be
re-processed after changing the embedding model.

The embedding engine and model selection can be doned in Admin Settings -> Documents -> Embedding section.

While in the Documents settings, also select Content Extraction Engine of choice. On my study I used containerized docling,
which is automatically started if using docker compose. Set the Engine to docling and url to `http://docling:5001` if
desired.

After the embedding settings have been finalized, go to the Workspace -> Knowledge and create new knowledge by pressing +.
Add the documents to the knowledge either by pressing + in UI or by drag-n-dropping.

## Tools - Medical Records

Go to the Workspace -> Tools and create new tool by pressing +. 
Add tool name, description and replace the template content with
the contents of [`tools/medical_records.py`](tools/medical_records.py).

You can now use the tool with any model which supports tools. You can see usage instructions in [Open WebUI documentation](https://docs.openwebui.com/features/plugin/tools/).

Note: Current implementation requires that the name of each user in OpenWebUI system must
match the UUID of the patient resource in the FHIR document if the medical history
functionality is needed.
