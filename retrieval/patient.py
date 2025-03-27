#!/usr/bin/env python3

import os
import logging
import datetime

import database


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Patient:

    def __init__(self, patient_id: str):
        """
        Patient class constructor.
        """
        self.db = database.Database()
        self.id = patient_id

        # Fetch basid details from the patients table
        query = f"SELECT date_of_birth, deceased_at, gender, email FROM patients WHERE id = %s"
        logger.debug(query)
        data = (self.id,)
        self._date_of_birth, self._deceased_at, self._gender, self._email = self.db.db_execute(query, data)[0]

    def date_of_birth(self):
        return self._date_of_birth

    def age(self):
        # Calculate current age if patient is alive and age when deceased if patient is dead.
        if self._deceased_at is None:
            now = datetime.datetime.now()
        else:
            now = datetime.datetime.fromisoformat(self._deceased_at).replace(tzinfo=None)
        age = now.year - self._date_of_birth.year
        if self._date_of_birth.month > now.month or (self._date_of_birth.month == now.month and self._date_of_birth.day > now.day):
            # If the birthday is still in future for the current year
            age -= 1
        return age

    def gender(self):
        return self._gender

    def email(self):
        return self._email

    def allergies(self, only_active: bool = True) -> dict[list[str]]:
        """
        Retrieves allergies for the patient.
        """

        # Define the query to retrieve allergies for the patient
        _where = ["patient_id = %s", "type = 'allergy'"]
        if only_active:
            _where.append("clinical_status = 'active'")
        _where = " AND ".join(_where)
        query = f"SELECT asserted_date, clinical_status, category, criticality, display FROM allergy_intolerances WHERE {_where} ORDER BY asserted_date"
        logger.debug(query)

        data = (self.id,)
        result = self.db.db_execute(query, data)

        strings = []
        d = {}
        for row in result:
            logger.debug(row)
            # Edit the display
            display = row[4].removeprefix("Allergy to ").removesuffix(" allergy").capitalize()
            # Format the string
            if row[3] == "high":
                criticality = "severe"
            elif row[3] == "low":
                criticality = "mild"
            else:
                criticality = row[3]
            s = f"{display} ({criticality})"
            if row[2] not in d:
                d[row[2]] = []
            d[row[2]].append(s)
            strings.append(s)
        return d

    def encounters(self):
        _where = ["patient_id = %s",]
        data = (self.id,)
        _where = " AND ".join(_where)
        query = f"SELECT id, class, type, period_start, period_end-period_start duration, reason_display FROM encounters WHERE {_where} ORDER BY period_start"
        logger.debug(query)
        result = self.db.db_execute(query, data)
        return [{
            "id": row[0],
            "class": row[1],
            "type": row[2],
            "period_start": row[3],
            "duration": row[4],
            "reason": row[5] if row[5] is not None else "Not specified",
        } for row in result]

    def conditions(self, encounter_id: str = None):
        _where = ["patient_id = %s",]
        data = (self.id,)
        if encounter_id is not None:
            _where.append("encounter_id = %s")
            data = (*data, encounter_id,)
        _where = " AND ".join(_where)
        query = f"SELECT id, encounter_id, clinical_status, verification_status, onset_date, abatement_data abatement_date, code_display FROM conditions WHERE {_where} ORDER BY onset_date"
        logger.debug(query)

        result = self.db.db_execute(query, data)
        return [{
            "id": row[0],
            "encounter_id": row[1],
            "clinical_status": row[2],
            "verification_status": row[3],
            "onset_date": row[4],
            "abatement_date": row[5],
            "code_display": row[6],
        } for row in result]

    def observations(self, encounter_id: str = None):
        _where = ["patient_id = %s",]
        data = (self.id,)
        if encounter_id is not None:
            _where.append("encounter_id = %s")
            data = (*data, encounter_id,)
        _where = " AND ".join(_where)
        query = f"SELECT id, encounter_id, observation_date, status, display, value, unit FROM observations WHERE {_where} ORDER BY observation_date"
        logger.debug(query)

        result = self.db.db_execute(query, data)
        return [{
            "id": row[0],
            "encounter_id": row[1],
            "observation_date": row[2],
            "status": row[3],
            "display": row[4],
            "value": row[5],
            "unit": row[6],
        } for row in result]

    def procedures(self, encounter_id: str = None, condition_id: str = None):
        _where = ["patient_id = %s",]
        data = (self.id,)
        if encounter_id is not None:
            _where.append("encounter_id = %s")
            data = (*data, encounter_id,)
        if condition_id is not None:
            _where.append("condition_id = %s")
            data = (*data, condition_id,)
        _where = " AND ".join(_where)
        query = f"SELECT encounter_id, condition_id, status, performed_date, performed_date_end, code_display FROM procedures WHERE {_where} ORDER BY performed_date"
        logger.debug(query)

        result = self.db.db_execute(query, data)
        return [{
            "encounter_id": row[0],
            "condition_id": row[1],
            "status": row[2],
            "performed_date": row[3],
            "performed_date_end": row[4],
            "code_display": row[5],
        } for row in result]

    def care_plans(self, encounter_id: str = None, condition_id: str = None):
        _where = ["patient_id = %s",]
        data = (self.id,)
        if encounter_id is not None:
            _where.append("encounter_id = %s")
            data = (*data, encounter_id,)
        if condition_id is not None:
            _where.append("condition_id = %s")
            data = (*data, condition_id,)
        _where = " AND ".join(_where)
        query = f"SELECT encounter_id, status, category_display, period_start_date, period_end_date, details FROM care_plans WHERE {_where} ORDER BY period_start_date"
        logger.debug(query)

        result = self.db.db_execute(query, data)
        return [{
            "encounter_id": row[0],
            "status": row[1],
            "category_display": row[2],
            "period_start_date": row[3],
            "period_end_date": row[4],
            "details": row[5],
        } for row in result]

    def immunizations(self, encounter_id: str = None):
        _where = ["patient_id = %s", "was_given IS TRUE",]
        data = (self.id,)
        if encounter_id is not None:
            _where.append("encounter_id = %s")
            data = (*data, encounter_id,)
        _where = " AND ".join(_where)
        query = f"SELECT encounter_id, date, status, vaccine_display FROM immunizations WHERE {_where}"
        logger.debug(query)

        result = self.db.db_execute(query, data)
        return [{
            "encounter_id": row[0],
            "date": row[1],
            "status": row[2],
            "vaccine_display": row[3],
        } for row in result]

    def medications(self, encounter_id: str = None):
        _where = ["patient_id = %s",]
        data = (self.id,)
        if encounter_id is not None:
            _where.append("encounter_id = %s")
            data = (*data, encounter_id,)
        _where = " AND ".join(_where)
        query = f"SELECT encounter_id, date_written, medication_display, dosage_instruction FROM medication_requests WHERE {_where}"
        logger.debug(query)

        result = self.db.db_execute(query, data)
        return [{
            "encounter_id": row[0],
            "date_written": row[1],
            "medication_display": row[2],
            "dosage_instruction": row[3],
        } for row in result]


if __name__ == "__main__":
    # Test the module
    pass
