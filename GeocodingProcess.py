import requests
import shapely
from flair.data import Sentence
from flair.nn import Classifier
import logging
import time

tagger = Classifier.load('ner')


def use_geocode_service(text):
    try:
        time.sleep(60)  # sleep for a minute
        res = requests.get("https://geocode.xyz/location", params={"scantext": text, "region": "AU", "json": 1})
        logging.debug(res)
        res_json = res.json()
        logging.debug(res_json)
        return shapely.geometry.Point(res_json['latt'], res_json['longt'])
    except:
        print("issue in geocoding using API")
    return None

def use_google_geocode_service(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "Your_API",  # Replace with your actual API key
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        return latitude, longitude
    else:
        return None

def find_location_names(text):
    sentence = Sentence(text)
    tagger.predict(sentence)
    unique_location_names = set()

    if 'ner' in sentence.annotation_layers.keys():
        ner_tags = sentence.annotation_layers['ner']
        for tag in ner_tags:
            if tag.value == 'LOC':
                unique_location_names.add(tag.data_point.text)

    return list(unique_location_names)


def names_to_coordinates(unique_location_names):
    # convert location names to latitude and longitude
    # return a list of latitude and longitude pairs
    # Convert location names to coordinates
    coordinates_dict = {}
    for location_name in unique_location_names:
        response = requests.get("https://nominatim.openstreetmap.org/search",
                                params={"q": location_name, "format": "json",
                                        "countrycodes": "au", "viewbox": "140.0,-39.0,150.0,-33.0"})
        if response.json():
            coordinates_dict[location_name] = response.json()[0]["lat"], response.json()[0]["lon"]
    return coordinates_dict


def choose_the_best_guess(texts, coordinates_dict):
    # choose the best guess of the location
    # return only one latitude and longitude pairs
    if coordinates_dict == {}: return []

    # if there is only one guess, return the coordinates of that guess
    if len(coordinates_dict) == 1:
        return list(coordinates_dict.values())[0]
    # if there are multiple guesses, choose the one that is closest to the beginning of the text
    else:
        # find the location name that is closest to the beginning of the text
        location_name = ""
        print(coordinates_dict)
        min_index = 100000
        for key in coordinates_dict.keys():
            index = texts.find(key)
            if index != -1 and index < min_index:
                min_index = index
                location_name = key
        return coordinates_dict[location_name]


def dict_to_shapely(best_guess):
    # create a shapely point object from the best guess
    point = shapely.geometry.Point(best_guess[1], best_guess[0])
    return point


def point_to_shapely(text):
    # create a shapely point object from the best guess
    location_names = find_location_names(text)
    if not location_names:
        print("No location names found.")
    else:
        print(location_names)
        coordinates_dict = names_to_coordinates(location_names)
        print(coordinates_dict)
        if coordinates_dict == {}:
            print("No coordinates found.")
        else:

            # choose the best guess of the location
            # return only one latitude and longitude pairs
            best_guess = choose_the_best_guess(text, coordinates_dict)

            # create a shapeley point object from the best guess
            point = dict_to_shapely(best_guess)
            return point


if __name__ == "__main__":
    text = "The VHI of H7822-1904 was located in Melbourne, Australia, specifically in the half acre lot 8 of " \
           "section 5 which was sold to John Batman in the second Melbourne land sales that took place in November " \
           "of 1837."

    point = point_to_shapely(text)
    print(point)
