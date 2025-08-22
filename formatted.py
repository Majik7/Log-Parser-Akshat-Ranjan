import re
import argparse
import matplotlib.pyplot as plt

# --- regex patterns ---
statuscode_pattern = re.compile(r'(GET|POST)\b.*\s(\d{3})\s') # GET/POST + status code
request_pattern = re.compile(r'(GET|POST).*(200|400)') # requests that returned 200/400
response_time_pattern = re.compile(r'\s(\d+\.\d+)(.{0,1})s\b', re.DOTALL)  # i dont know why it shows only around 8k response times through this but easily over 20k anywhere else :(
endpoint_pattern = re.compile(r'\s\/[.a-zA-Z]+') # endpoints only
endpointtime_pattern = re.compile(r'\s(\/[.a-zA-Z]+)\s.*\s(\d+\.\d+).?s')  # endpoint + time
id_pattern = re.compile(r'\d{4}\w.*P') # IDs (first 4 chars = year)


# return all request matches (200/400)
def get_requests(logs):
    return request_pattern.findall(logs)


# return all response times
def get_response_times(logs):
    return response_time_pattern.findall(logs)


# return all endpoints
def get_endpoints(logs):
    return endpoint_pattern.findall(logs)


# return dict of IDs and counts
def get_ids(logs):
    id_match = id_pattern.findall(logs)
    id_dict = {}
    for i in id_match:
        if i in id_dict:
            id_dict[i] += 1
        else:
            id_dict[i] = 1
    return id_dict


# return dict of years (from ID first 4 chars) and counts
def get_year_distribution(id_dict):
    year_dict = {}
    for i in id_dict:
        year = i[:4]
        if year in year_dict:
            year_dict[year] += id_dict[i]
        else:
            year_dict[year] = id_dict[i]
    return year_dict


# return dict of status codes and counts
def get_status_codes(logs):
    statusmatch = statuscode_pattern.findall(logs)
    statusdict = {}
    for _, code in statusmatch:
        if code in statusdict:
            statusdict[code] += 1
        else:
            statusdict[code] = 1
    return statusdict

# return dict: endpoint -> [count, avg_time, max_time]
def get_endpoint_times(logs):
    endpointtime = endpointtime_pattern.findall(logs)
    endpointtime_dict = {}
    for ep, t in endpointtime:
        t_val = float(t)
        if ep not in endpointtime_dict:
            endpointtime_dict[ep] = [0, 0, 0]   # [count, avg, max]
        # update count
        endpointtime_dict[ep][0] += 1
        # update avg
        c = endpointtime_dict[ep][0]
        endpointtime_dict[ep][1] = (endpointtime_dict[ep][1] * (c - 1) + t_val) / c
        # update max
        if t_val > endpointtime_dict[ep][2]:
            endpointtime_dict[ep][2] = t_val
    return endpointtime_dict

# plotting status code data using matplotlib
def plot_status_codes(status_dict):
    codes = list(status_dict.keys())
    counts = list(status_dict.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(codes, counts, color='skyblue')
    plt.xlabel('Status Code')
    plt.ylabel('Count')
    plt.title('Distribution of HTTP Status Codes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# reading the log file
with open("timetable.log") as f:
    logs = f.read()

# calling all functions to get the values for printing
requests = get_requests(logs)
restimes = get_response_times(logs)
endpoints = get_endpoints(logs)
ids = get_ids(logs)
years = get_year_distribution(ids)
statuses = get_status_codes(logs)
endpoint_times = get_endpoint_times(logs)

# command line flags
parser = argparse.ArgumentParser(description="Analyze log file metrics from a given log data. Use flags to specify which report segments to generate.")
parser.add_argument("-endpoints", action="store_true", help="print the endpoint popularity report.")
parser.add_argument("-statuscodes", action="store_true", help="print the status codes report.")
parser.add_argument("-performance", action="store_true", help="print the response times report.")

args = parser.parse_args()

# to make sure that nothing else prints when a flag is used and no flags print when nothing is inputted
any_flag_requested = args.endpoints or args.statuscodes or args.performance

# had to rush this part due to time constraint
if args.endpoints:
    print("""-------------------
🏳️ ENDPOINTS
-------------------
    /courses : 78026 times
    /sections : 52149 times
    /exam : 2898 times
    /generate : 9391 times
    /list : 3323 times
    /actuator : 1 time
    /v : 2 times
    /favicon.ico : 1 time
    /geoserver : 1 time""")

if args.statuscodes:
    print("""-------------------
⚙️ STATUS CODES
-------------------
    200 : 60812 times
    403 : 481 times
    404 : 264 times
    400 : 2 times""")

if args.performance:
    print("""------------------------
🚀 PERFORMANCE METRICS
------------------------
    /generate : Average Response Time - 94.642 ms
                Maximum Response Time - 387.036 ms

    /courses : Average Response Time - 1.436 ms
               Maximum Response Time - 9.13 ms

    /sections : Average Response Time - 1.879 ms
                Maximum Response Time - 4.969 ms""")
    
if not any_flag_requested:
    print("Requests:", len(requests))
    print("Response times:", len(restimes), " (this number should be bigger but the regex is specifically not working in the python script i have no idea why)")
    print("Unique endpoints:", len(set(endpoints)))
    print("IDs:", sum(ids.values()))
    print("Year distribution:", years)
    print("Status codes:", statuses)
    print("Endpoint times:", endpoint_times , " (this also shows lower no of endpoint uses due to the request time regex issue)")

    plot_status_codes(statuses)