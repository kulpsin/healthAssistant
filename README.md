# Fresh install instructions
```bash
git clone https://github.com/kulpsin/virtualDoc
cd virtualDoc
cp .env.template .env
# Edit .env file
docker compose up -d --build
```
Create admin account.



# Ollama models

You can follow [these instructions](https://github.com/ollama/ollama/blob/main/docs/import.md) to import a model (which you have downloaded before) into ollama. Note that instead of `ollama create my-model`, you need to run the command in container: `docker exec -it ollama ollama create my-model`.

You can also browse [Ollama library](https://ollama.com/library) for their hosted models and install them with ollama run command.

# Add FHIR data to database

You can use for example the following curl command to insert a FHIR-json into database:

```bash
curl -d @path/to/json/0006a28d-fb47-40cf-afa8-32360c384798.json -H 'Content-Type: application/json' localhost:8000/reindex
```

Note that FHIR JSON format is not fully supported yet, only following files have been tested to work:
- `0006a28d-fb47-40cf-afa8-32360c384798.json`
- `000b837b-1ee8-4eb1-aea6-0469f1128e43.json`
- `000dc563-9b0a-4890-9c09-a61314ba9e5c.json`
- `000fe04a-7a4e-43cf-95f6-feaa1ffa9fb1.json`
- `0124a570-1e58-4217-b515-b4ef8917744f.json`

# Tools - Medical Records

In Open WebUI, go to the Workspace -> Tools and create new tool by pressing +. Add tool name, description and replace the template content with the contents of [`tools/medical_records.py`](tools/medical_records.py).

You can now use the tool with any model which supports tools. You can see usage instructions in [Open WebUI documentation](https://docs.openwebui.com/features/plugin/tools/).