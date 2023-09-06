import DBHandler as db_handler

def fetch_all_reports():
    raw_models = db_handler.get_all_raw_models()
    refined_models = [r[0:6] for r in raw_models]
    for idx, r in enumerate(raw_models):
        lat, lon = r[8].replace("POINT(", "").replace(")", "").strip().split(" ")
        refined_models[idx] += (lat, lon,)
    print(refined_models)
    return refined_models
