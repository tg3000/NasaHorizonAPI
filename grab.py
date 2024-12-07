import requests
import io
import sys
import json

def create_request_file(target_body: str, center_body: str, start_time: str, end_time: str, step_size: str):
    command = "!$$SOF\n"
    planet_ids = {
        "sun" : "@10",
        "mercury" : "@199",
        "venus" : "@299",
        "earth" : "@399",
        "mars" : "@499",
        "jupiter" : "@599",
        "saturn" : "@699",
        "uranus" : "@799",
        "neptune" : "@899",
    }

    dict = {
        "COMMAND" : planet_ids.get(target_body),
        "OBJ_DATA" : "YES",
        "MAKE_EPHEM" : "YES",
        "TABLE_TYPE" : "V",
        "CENTER" : planet_ids.get(center_body),
        "START_TIME" : start_time,
        "STOP_TIME" : end_time,
        "STEP_SIZE" : step_size,
        "OUT_UNITS" : "KM-S",
        "VEC_TABLE" : "2",
        "VEC_LABELS" : "NO",
        "CSV_FORMAT" : "YES",
    }
    for val in dict.items():
        command += val[0] + "='" + val[1] + "'"


    command += "!$$EOF"
    return io.StringIO(command)

def prep_output(output: str) -> str:
    output = output.split("$$SOE")[1]
    output = output.split("$$EOE")[0]
    output = output.split("\n")
    output.pop(0)
    output.pop()
    states = []
    for val in output:
        arr = val.split(", ")
        _, date, time = tuple(arr[1].split(" "))
        x, y, z = (arr[2], arr[3], arr[4])
        vx, vy, vz = (arr[5], arr[6], arr[7])
        states.append(State(date, time, Vector(x, y, z), Vector(vx, vy, vz)))
    return states

class Vector(dict):
    def __init__(self, x: str, y: str, z: str):
        dict.__init__(self, x=x, y=y, z=z)

class State(dict):
    def __init__(self, date: str, time: str, coordinate: Vector, speeds: Vector):
        dict.__init__(self, date=date, time=time, coordinate=coordinate, speeds=speeds)


def main(target_body: str, center_body: str, start_time: str, end_time: str, step_size: str, raw=False):
    f = create_request_file(target_body.lower(), center_body.lower(), 
        start_time, end_time, step_size)

    output_name = target_body.lower() + "_" + start_time + "_" + end_time
    if raw:
        output_name += "_raw"
    output_name += ".txt"
    out = open(output_name, "w")
    url = 'https://ssd.jpl.nasa.gov/api/horizons_file.api'
    r = requests.post(url, data={'format':'text'}, files={'input': f})
    if raw:
        out.write(r.text)
    else:
        json.dump(prep_output(r.text), out)

    out.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], 
        sys.argv[3], sys.argv[4], sys.argv[5])
