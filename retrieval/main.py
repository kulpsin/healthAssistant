#!/usr/bin/env python3

"""
Simple API for Retrieval.


Author: Olli Puhakka
"""
import datetime
import logging
logger = logging.getLogger(__file__)
from fastapi import FastAPI, Request
from pydantic import BaseModel

import index_fhir
import patient

class Fhir(BaseModel):
    type: str
    entry: list
    resourceType: str

class SearchRequest(BaseModel):
    resourceType: str
    query: str
    searchParams: dict


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/reindex")
def reindex_jsons(item: Fhir):
    """
    Reindex the JSONs in the FHIR item.
    """
    logger.info(f"Reindexing JSONs in FHIR item of type {item.resourceType}")
    item_dict = item.dict()
    try:
        index_fhir.parse_fhir(item_dict['entry'])
    except NotImplementedError as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}
    return {"status":"success"}


@app.post("/search")
def search_database(data: SearchRequest):
    """
    Search the database for the given FHIR item.
    """
    pass

@app.get("/patient/{id}/allergies")
def get_patient_allergies(id: str):
    """
    Retrieve allergies for a specific patient.

    Example: {"food":["Peanuts (severe)","Wheat (severe)","Eggs (mild)","Soya (mild)","Tree pollen (severe)","Grass pollen (mild)","Dander (animal) (severe)","Mould (severe)"]}
    """
    p = patient.Patient(id)
    allergies = p.allergies()
    if allergies is None:
        return {"error": "Patient allergies not found"}
    return allergies

@app.get("/patient/{id}/report")
def get_patient_encounters(id: str, request: Request):
    """
    Retrieve full report of all patient encounters.
    """

    # Create a patient instance for the specific patient.
    p = patient.Patient(id)

    report = [
        f"Patient is {p.age()} year old {p.gender()}.",
        f"**Date of Birth:** {p.date_of_birth()}",
        "",
        "## Medical encounters",
    ]
    for encounter in p.encounters():
        report.append(f"### {encounter['class'].capitalize()} - {encounter['type']}")
        report.append(f"- **Date**: {encounter['period_start'].replace(tzinfo=None)}")
        if encounter['duration'] > datetime.timedelta(hours=1):
            report.append(f"- **Duration**: {encounter['duration']}")
        report.append(f"- **Reason**: {encounter['reason']}")

        # Add conditions to the report:
        conditions = [
            condition['code_display'] if condition['abatement_date'] is None
            else f"{condition['code_display']} (until {condition['abatement_date'].replace(tzinfo=None)})"
            for condition in p.conditions(encounter_id=encounter['id'])
        ]
        if conditions:
            report.append(f"- **Conditions confirmed:** {", ".join(conditions)}")

        # Add observations to the report
        observations = p.observations(encounter_id=encounter['id'])
        if observations:
            report.append("- **Observations**:")
        for observation in observations:
            for i in range(len(observation['display'])):
                report.append(f"  - {observation['display'][i]}: {observation['value'][i]} {observation['unit'][i]}")

        # Add procedures to the report
        procedures = p.procedures(encounter_id=encounter['id'])
        if procedures:
            report.append("- **Procedures**:")
        for procedure in procedures:
            report.append(f"  - {procedure['code_display']}")

        # Add care plans to the report
        care_plans = p.care_plans(encounter_id=encounter['id'])
        if care_plans:
            report.append("- **Care Plans**:")
        for care_plan in care_plans:
            report.append(f"  - {care_plan['details']} (Status: {care_plan['status']})")

        # Add immunizations to the report
        immunizations = p.immunizations(encounter_id=encounter['id'])
        if immunizations:
            report.append("- **Immunizations**:")
        for immunization in immunizations:
            report.append(f"  - {immunization['vaccine_display']}")

        # Add medication to the report
        medications = p.medications(encounter_id=encounter['id'])
        if medications:
            report.append("- **Medications**:")
        for medication in medications:
            report.append(f"  - {medication['medication_display']}")

        report.append("")
    return "\n".join(report)
