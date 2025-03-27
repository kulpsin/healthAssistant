#!/usr/bin/env python3

"""
This script is used to index FHIR resources to a database.
It reads the FHIR resources from a json file, parses them,
and inserts them into the database.

TODO: Handle timezones... Current functionality:
- Local time is saved in database
- Reason: patient is living in local time, and it might be beneficial to differentiate
  if the patient seeked medical assistance 3pm or 3am
- This is just a PoC with synthetic data, so the dates and times doesn't really matter

Author: Olli Puhakka
"""
import os
import argparse
import json
import psycopg2
import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Patient:
    database_connection = None

    def __init__(self, id, gender, birth_date, deceased_at, email):
        # TODO: description has age-> age changes over time so this should be calculated in tool instead or as virtual database column.

        # Initialize the db:
        if self.database_connection is None:
            self.__init_database__()

        # Initialize the patient
        self.db_add_patient(id, gender, birth_date, deceased_at, email)
        self.patient_id = id

        # Calculate current age if patient is alive and age when deceased if patient is dead.
        if deceased_at is None:
            now = datetime.datetime.now()
        else:
            now = datetime.datetime.fromisoformat(deceased_at).replace(tzinfo=None)
        age = now.year - birth_date.year
        if birth_date.month > now.month or (birth_date.month == now.month and birth_date.day > now.day):
            # If the birthday is still in future for the current year
            age -= 1
        description = f'Patient is {age} year old {gender}'
        logger.info(description)

    @classmethod
    def __init_database__(cls):
        cls.database_connection = psycopg2.connect(
            host     = os.environ['POSTGRES_HOST'],
            port     = os.environ['POSTGRES_PORT'],
            database = os.environ['POSTGRES_DB'],
            user     = os.environ['POSTGRES_TOOL_USER'],
            password = os.environ['POSTGRES_TOOL_PASSWORD'],
        )
        return cls.database_connection

    def _db_execute(self, query: str, data: tuple):
        """
        Execute the query with data.
        """
        try:
            with self.database_connection:
                with self.database_connection.cursor() as curs:
                    curs.execute(query, data)
        except psycopg2.InterfaceError as e:
            # connection already closed ?
            # Reinitialize connection and try again
            self.__init_database__()
            with self.database_connection:
                with self.database_connection.cursor() as curs:
                    curs.execute(query, data)

    def db_add_patient(self, id, gender, birth_date, deceased_at, email):
        """
        Inserts patient data into the DB.
        """
        self._db_execute(
            "INSERT INTO patients (id, date_of_birth, deceased_at, gender, email) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (id, birth_date, deceased_at, gender, email),
        )

    def db_add_encounter(self, id, patient_id, status, class_, type, period_start, period_end, reason):
        """
        Inserts encounter data into the DB.
        """
        self._db_execute(
            """INSERT INTO encounters (id, patient_id, status, class, type, period_start, period_end, reason_display)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (id, patient_id, status, class_, type, period_start, period_end, reason),
        )


    def db_add_allergy_intolerance(self, patient_id, asserted_date, clinical_status, type, category, criticality, display):
        """
        Inserts allergy or intolerance into the DB.
        """
        self._db_execute(
            """INSERT INTO allergy_intolerances (patient_id, asserted_date, clinical_status, type, category, criticality, display)
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (patient_id, asserted_date, clinical_status, type, category, criticality, display),
        )

    def db_add_condition(self, id, patient_id, encounter_id, clinical_status, verification_status, onset_date, abatement_data, code_display):
        """
        Inserts condition into the DB.
        """
        self._db_execute(
            """INSERT INTO conditions (id, patient_id, encounter_id, clinical_status, verification_status, onset_date, abatement_data, code_display)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (id, patient_id, encounter_id, clinical_status, verification_status, onset_date, abatement_data, code_display),
        )

    def db_add_observation(self, id, patient_id, encounter_id, observation_date, status, display, value, unit):
        """
        Inserts observation into the DB.
        """
        self._db_execute(
            """INSERT INTO observations (id, patient_id, encounter_id, observation_date, status, display, value, unit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (id, patient_id, encounter_id, observation_date, status, display, value, unit),
        )

    def db_add_careplan(self, patient_id, encounter_id, status, category_display, period_start_date, period_end_date, details):
        """
        Inserts care-plan into the DB.
        """
        self._db_execute(
            """INSERT INTO care_plans (patient_id, encounter_id, status, category_display, period_start_date, period_end_date, details)
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (patient_id, encounter_id, status, category_display, period_start_date, period_end_date, details),
        )

    def db_add_medication_request(self, patient_id, encounter_id, date_written, medication_display, dosage_instruction):
        """
        Inserts medication request into the DB.
        """
        self._db_execute(
            """INSERT INTO medication_requests (patient_id, encounter_id, date_written, medication_display, dosage_instruction)
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (patient_id, encounter_id, date_written, medication_display, dosage_instruction),
        )

    def db_add_procedure(self, patient_id, encounter_id, condition_id, status, performed_date, performed_date_end, code_display):
        """
        Inserts procedure into the DB.
        """
        self._db_execute(
            """INSERT INTO procedures (patient_id, encounter_id, condition_id, status, performed_date, performed_date_end, code_display)
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (patient_id, encounter_id, condition_id, status, performed_date, performed_date_end, code_display),
        )

    def db_add_immunization(self, patient_id, encounter_id, date, status, vaccine_display, was_given, primary_source):
        """
        Inserts immunization into the DB.
        """
        self._db_execute(
            """INSERT INTO immunizations (patient_id, encounter_id, date, status, vaccine_display, was_given, primary_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (patient_id, encounter_id, date, status, vaccine_display, was_given, primary_source),
        )


def datetime_from_isoformat(dt: str | None) -> datetime.datetime:
    """
    Create a datetime object from iso date and return it.
    - Timezone information is removed, using local time here
    - Adding 7 years to each date, to artificially make the dataset appear more recent
    """
    return datetime.datetime.fromisoformat(dt).replace(tzinfo=None) + datetime.timedelta(days=7*365)


def parse_fhir(entry: dict):
    """
    Parse the given FHIR resource data and save to database.

    @param entry: The FHIR resource data to parse.
    """

    patient = None
    for row in entry:
        res = row['resource']
        match res['resourceType']:
            case 'Patient':
                patient = Patient(
                    res['id'],
                    res['gender'],
                    datetime_from_isoformat(res['birthDate']),
                    datetime_from_isoformat(res['deceasedDateTime']) if 'deceasedDateTime' in res else None,
                    f"{res['name'][0]['given'][0]}.{res['name'][0]['family']}@localhost",  # email
                )

            case 'Encounter':
                patient.db_add_encounter(
                    res['id'],
                    res['patient']['reference'].split(':')[2],
                    res['status'],
                    res['class']['code'],
                    res['type'][0]['text'],
                    datetime_from_isoformat(res['period']['start']),
                    datetime_from_isoformat(res['period']['end']),
                    res['reason']['coding'][0]['display'] if 'reason' in res else None,
                )

            case 'Observation':
                # id, patient_id, encounter_id, observation_date, status, display, value, unit
                display = []
                value = []
                unit = []
                if 'component' in res:
                    for item in res['component']:
                        display.append(item['code']['coding'][0]['display'])
                        value.append(item["valueQuantity"]["value"])
                        unit.append(item["valueQuantity"]["unit"])
                elif 'valueQuantity' in res:
                    display.append(res['code']['coding'][0]['display'])
                    value.append(res["valueQuantity"]["value"])
                    unit.append(res["valueQuantity"]["unit"])
                else:
                    raise NotImplementedError(f"{res['resourceType']} not fully implemented yet!")

                patient.db_add_observation(
                    res['id'],
                    res['subject']['reference'].split(':')[2],
                    res['encounter']['reference'].split(':')[2],
                    datetime_from_isoformat(res['effectiveDateTime']),
                    res['status'],
                    display,
                    value,
                    unit,
                )
                continue
                # This is not yet implemented:
                if 'valueCodeableConcept' in res:
                    value = f'{res["code"]["coding"][0]["display"]}: {res["valueCodeableConcept"]["coding"][0]["display"]}' 
                    print(f'{res["resourceType"]}: {value} {display} in {time_at}')

            case 'Condition':
                # id, patient_id, encounter_id, clinical_status, verification_status, onset_date, abatement_data, code_display
                patient.db_add_condition(
                    res['id'],
                    res['subject']['reference'].split(':')[2],
                    res['context']['reference'].split(':')[2],
                    res['clinicalStatus'],
                    res['verificationStatus'],
                    datetime_from_isoformat(res['onsetDateTime']),
                    datetime_from_isoformat(res['abatementDateTime']) if 'abatementDateTime' in res else None,
                    res['code']['coding'][0]['display']
                )

            case 'Procedure':
                # patient_id, encounter_id, condition_id, status, performed_date, code_display
                patient.db_add_procedure(
                    res['subject']['reference'].split(':')[2],
                    res['encounter']['reference'].split(':')[2],
                    res['reasonReference']['reference'].split(':')[2] if 'reasonReference' in res else None,
                    res['status'],
                    datetime_from_isoformat(res['performedDateTime'] if 'performedDateTime' in res else res['performedPeriod']['start']),
                    datetime_from_isoformat(res['performedPeriod']['end']) if 'performedPeriod' in res else None,
                    res['code']['coding'][0]['display'],
                )

            case 'DiagnosticReport':
                # Doesn't seem to contain valuable information
                continue
                raise NotImplementedError(f"{res['resourceType']} not implemented yet!")

            case 'Immunization':
                # patient_id, encounter_id, date, status, vaccine_display, was_given, primary_source
                patient.db_add_immunization(
                    res['patient']['reference'].split(':')[2],
                    res['encounter']['reference'].split(':')[2],
                    datetime_from_isoformat(res['date']),
                    res['status'],
                    res['vaccineCode']['coding'][0]['display'],
                    not res['wasNotGiven'],
                    res['primarySource'],
                )

            case 'CarePlan':
                # TODO: Check that all get saved...
                activities = []
                for item in res['activity']:
                    if item['detail']['status'] not in ('in-progress', 'completed'):
                        raise NotImplementedError(f"Activity status {item['detail']['status']} for {res['resourceType']} not implemented yet!")
                    activities.append(item['detail']['code']['coding'][0]['display'])
                if len(activities) < 2:
                    details = activities[0]
                else:
                    # Quick'n'dirty concat: 'Food allergy diet and Allergy education'
                    details = ", ".join(activities[:-1]) + " and " + activities[-1]

                patient.db_add_careplan(
                    res['subject']['reference'].split(':')[2],
                    res['context']['reference'].split(':')[2],
                    res['status'],
                    res['category'][0]['coding'][0]['display'],
                    datetime_from_isoformat(res['period']['start']),
                    datetime_from_isoformat(res['period']['end']) if 'end' in res['period'] else None,
                    details,
                )

            case 'MedicationRequest':
                # TODO: Special dosage instructions
                if len(res['dosageInstruction']) > 1:
                    raise NotImplementedError(f"Dosage Instruction > 1 {res['resourceType']} not implemented yet!")
                if len(res['dosageInstruction']) == 0 or len(res['dosageInstruction'][0]) == 0:
                    dosage_instruction = None
                elif 'asNeededBoolean' not in res['dosageInstruction'][0]:
                    logger.error(f"{str(res['dosageInstruction'][0])}")
                    raise NotImplementedError(f"Dosage Instruction {res['resourceType']} not implemented yet!")
                elif res['dosageInstruction'][0]['asNeededBoolean']:
                    dosage_instruction = 'as needed'
                elif 'timing' in res['dosageInstruction'][0]:
                    doseage = res['dosageInstruction'][0]
                    if doseage['timing']['repeat']['period'] == 1 and doseage['timing']['repeat'] ['periodUnit']== "d":
                        # 1 dose 2 times per day
                        dosage_instruction = f"{doseage['doseQuantity']['value']} dose {doseage['timing']['repeat']['frequency']} times per day"
                    elif doseage['timing']['repeat'] ['periodUnit']== "h" and doseage['timing']['repeat']['frequency'] == 1:
                        # x dose every n hours
                        dosage_instruction = f"{doseage['doseQuantity']['value']} dose every {doseage['timing']['repeat']['period']} hours"
                    else:
                        raise NotImplementedError(f"Dosage Instruction {res['resourceType']} not fully implemented yet!")
                else:
                    raise NotImplementedError(f"Final else Dosage Instruction {res['resourceType']} not implemented yet!")
                dosage_instruction
                patient.db_add_medication_request(
                    res['patient']['reference'].split(':')[2],
                    res['context']['reference'].split(':')[2],
                    datetime_from_isoformat(res['dateWritten']),
                    res['medicationCodeableConcept']['coding'][0]['display'],
                    dosage_instruction,
                )

            case 'AllergyIntolerance':
                patient.db_add_allergy_intolerance(
                    res['patient']['reference'].split(':')[2],
                    datetime_from_isoformat(res['assertedDate']),
                    res['clinicalStatus'],
                    res['type'],
                    res['category'][0],  # Saving only first category
                    res['criticality'],
                    res['code']['coding'][0]['display'],
                )

            case _:
                raise Exception(f'Not handled: {res["resourceType"]}')

def valid_json_file(path):
    """
    Check if the given path is a valid json file.
    """
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File {path} does not exist.")
    try:
        with open(path, 'r') as f:
            json.load(f)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"File {path} is not a valid json file.")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index FHIR resources to a database.")
    parser.add_argument("json_file", type=valid_json_file, help="Path to the json file containing the FHIR resources.")
    args = parser.parse_args()

    with open(args.json_file, 'r') as f:
        data = json.load(f)
    try:
        parse_fhir(data['entry'])
    except NotImplementedError as e:
        print(e)
    Patient.database_connection.close()