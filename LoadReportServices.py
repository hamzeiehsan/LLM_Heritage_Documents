import spacy
import dateparser
import os
import shapely
import re
import json

import LLMProcess as llm
import ExtractionPrompts as ps
import GeocodingProcess as geocoder
from HVConstants import (
    SOURCE_DIRECTORY,
    DOCUMENT_MAP
)

from KBModel import HVDataModel
import DBHandler as sqlDB

nlp = spacy.load("en_core_web_lg")


def analyze_all_documents(source_dir=SOURCE_DIRECTORY):
    all_files = os.listdir(source_dir)
    paths = []
    for file_path in all_files:
        print(file_path)
        file_extension = os.path.splitext(file_path)[1]
        source_file_path = os.path.join(source_dir, file_path)
        if file_extension in DOCUMENT_MAP.keys():
            paths.append(source_file_path)
    for p in paths:
        filter_argument = {"filter": {"source": p}}
        model = extract_info_from_doc(filter_argument, p)
        load_to_db(model)
        print("{} processed and information are extracted...".format(p))


def extract_info_from_doc(filter_argument, report):
    # ids
    ex_identifiers = identifiers_extraction(filter_argument)
    # location
    ex_location, additional = location_extraction(filter_argument)
    with open("output/{}.json".format(report.split("/")[-1]), "w") as fp:
        json.dump(additional, fp)

    # dates
    ex_dates = dates_extraction(filter_argument)
    # types
    ex_types = types_extraction(filter_argument)
    # significance
    ex_significance = significance_extraction(filter_argument)
    # summary
    ex_summary = summary_extraction(filter_argument)
    # additional
    ex_additional = additional_info_extraction(filter_argument)

    return HVDataModel(report=report, identifiers=ex_identifiers, location=ex_location, dates=ex_dates, types=ex_types,
                       significance=ex_significance, summary=ex_summary, additional=ex_additional)


def identifiers_extraction(filter_argument):
    ex_identifiers = {}
    # needs further work here.
    prompt = ps.P_ID_HPN
    resp = llm.answer_query_from_db(prompt,
                                    custom_format="answer in a sentence",
                                    search_kwargds=filter_argument)
    ex_identifiers['Permit ID'] = id_resolution(resp['answer'] + filter_argument['filter']['source'])
    return ex_identifiers


PERMIT_ID_PATTERNS = [r'H\d+-\d+', r'H\d+', r'\d+-\d+', r'\d+']


def id_resolution(text, patterns=PERMIT_ID_PATTERNS):
    for p in patterns:
        m = re.findall(p, text)
        if len(m) > 0:
            if len(m) < 3:
                return m
            return m[:3]
    return []


def dates_extraction(filter_argument):
    ex_dates = {}
    prompt = ps.P_REPORT_DATE + " " + ps.P_REPORT_DATE_A1
    resp = llm.answer_query_from_db(prompt,
                                    custom_format="answer in a paragraph", search_kwargds=filter_argument)
    print(resp)
    ex_dates['report_date'] = dates_extraction_process(resp['answer'])
    prompt = ps.P_EXCAV_DATE + " " + ps.P_EXCAV_DATE_A1
    resp = llm.answer_query_from_db(prompt,
                                    custom_format="answer in a paragraph", search_kwargds=filter_argument)
    print(resp)
    ex_dates['excavation_date'] = dates_extraction_process(resp['answer'])
    prompt = ps.P_COMP_DATE + " " + ps.P_COMP_DATE_A1
    resp = llm.answer_query_from_db(prompt,
                                    custom_format="answer in a paragraph", search_kwargds=filter_argument)
    print(resp)
    ex_dates['completion_date'] = dates_extraction_process(resp['answer'])
    return ex_dates


def dates_extraction_process(answer_text):
    doc = nlp(answer_text)
    times = []
    for ent in doc.ents:
        if ent.label_ == "DATE":
            time = dateparser.parse(ent.text)
            if time:
                times.append(time)
    if len(times) > 0:
        ex_dates = [t.strftime("%Y:%m:%d") for t in times]
        ex_dates = list(set(ex_dates))
        if len(ex_dates) > 3:
            return ex_dates[:3]
        return ex_dates
    else:
        return None


def location_extraction(filter_argument):
    additional_info = {}
    coordinates = None
    prompt = ps.P_LOCATION_A0
    resp = llm.answer_query_from_db(prompt,
                                    custom_format="describe address in one paragraph",
                                    search_kwargds=filter_argument)
    print(resp)
    ex_location = geocoder.point_to_shapely(resp['answer'])
    print(ex_location)
    additional_info[0] = {
        'paragraph': resp['answer'],
        'source': [str(s) for s in resp['source_documents']],
        'location': str(ex_location)
    }
    if ex_location is not None:
        additional_info[0]['api'] = str(geocoder.use_geocode_service(resp['answer']))
        coordinates = ex_location


    prompt = ps.P_LOCATION
    resp = llm.answer_query_from_db(prompt,
                                    custom_format="describe in one sentence using location names",
                                    search_kwargds=filter_argument)
    print(resp)
    ex_location = geocoder.point_to_shapely(resp['answer'])
    print(ex_location)
    additional_info[1] = {
        'paragraph': resp['answer'],
        'source': [str(s) for s in resp['source_documents']],
        'location': str(ex_location)
    }
    if ex_location is not None:
        additional_info[1]['api'] = str(geocoder.use_geocode_service(resp['answer']))
        if coordinates is None:
            coordinates = ex_location

    resp = llm.answer_query_from_db(ps.P_LOCATION_A2,
                                    custom_format="describe in one sentence using location names",
                                    search_kwargds=filter_argument)
    ex_location = geocoder.point_to_shapely(resp['answer'])
    print(ex_location)
    additional_info[2] = {
        'paragraph': resp['answer'],
        'source': [str(s) for s in resp['source_documents']],
        'location': str(ex_location)
    }
    if ex_location is not None:
        additional_info[2]['api'] = str(geocoder.use_geocode_service(resp['answer']))
        if coordinates is None:
            coordinates = ex_location
    resp = llm.answer_query_from_db(ps.P_LOCATION_A3,
                                    custom_format="describe in one sentence using location names",
                                    search_kwargds=filter_argument)
    ex_location = geocoder.point_to_shapely(resp['answer'])
    print(ex_location)
    additional_info[3] = {
        'paragraph': resp['answer'],
        'source': [str(s) for s in resp['source_documents']],
        'location': str(ex_location)
    }
    additional_info[3]['api'] = str(geocoder.use_geocode_service(resp['answer']))
    if ex_location is None:
        ex_location = shapely.geometry.Point(-37.8136, 144.9631)  # set a default for Melbourne!
    if coordinates is None:
        coordinates = ex_location
    return coordinates, additional_info


def types_extraction(filter_argument):
    custom_format = "answer in one sentence"
    prompt = ps.P_TYPES
    resp = llm.answer_query_from_db(prompt,
                                    custom_format=custom_format,
                                    search_kwargds=filter_argument)
    print(resp)
    return [resp['answer'].replace(custom_format, "")]


def significance_extraction(filter_argument):
    custom_format = "answer in a few sentences"
    prompt = ps.P_SIG
    resp = llm.answer_query_from_db(prompt,
                                    custom_format=custom_format,
                                    search_kwargds=filter_argument)
    print(resp)
    return resp['answer'].replace(custom_format, "")


def additional_info_extraction(filter_argument):
    ex_additional = {}  # simply to add more content here.
    return ex_additional


def summary_extraction(filter_argument):
    custom_format = "answer in one paragraph"
    prompt = ps.P_SUMMARY
    resp = llm.answer_query_from_db(prompt,
                                    custom_format=custom_format,
                                    search_kwargds=filter_argument)
    print(resp)
    return resp['answer'].replace(custom_format, "")


def load_to_db(model):
    print(model.toHTML())
    conn = sqlDB.create_connection()
    sqlDB.insert_into_db(model, conn)
    conn.close()
    print("Extracted information are persisted in the SQLite Database")


if __name__ == "__main__":
    print("starting to extract information from documents")
    analyze_all_documents()
