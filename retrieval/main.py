#!/usr/bin/env python3

"""
Simple API for Retrieval

Author: Olli Puhakka
"""
import logging
logger = logging.getLogger(__file__)
from fastapi import FastAPI
from pydantic import BaseModel
import index_fhir

class Fhir(BaseModel):
    type: str
    entry: list
    resourceType: str

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/reindex")
def reindex_jsons(item: Fhir):
    item_dict = item.dict()
    try:
        index_fhir.parse_fhir(item_dict['entry'])
    except NotImplementedError as e:
        logger.error(f"Error: {e}") 
        return {"error": str(e)}
    return {"status":"success"}

