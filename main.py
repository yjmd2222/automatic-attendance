import json

def load_json(traffic):
    with open(f'{traffic}.json', 'r') as fh:
        now = json.load(fh)
    with open(f'{traffic}_before.json', 'r') as fh:
        before = json.load(fh)
    return now, before

def timestamp_list(traffic, before):
    return {before[traffic][i]['timestamp']: i for i in range(len(before[traffic]))}

def append_json(traffic, timestamps, before, now):
    latest = dict(before)
    for i in range(len(now[traffic])):
        timestamp = now[traffic][i]['timestamp']
        if timestamp in timestamps:
            latest[traffic][timestamps[timestamp]] = now[traffic][i]
        else:
            latest[traffic].append(now[traffic][i])
    return latest

def sum_counts(latest, traffic):
    latest['count'] = sum(map(lambda x: int(x['count']), latest[traffic]))
    latest['uniques'] = sum(map(lambda x: int(x['uniques']), latest[traffic]))
    return latest

sort_key = lambda x: x['timestamp']

def merge_counts(timestamps, traffic_var):
    if len(timestamps) > 100:
        remove_this = []
        traffic_var.sort(key=sort_key)
        for i in range(len(timestamps) - 35):
            traffic_var[i]['timestamp'] = traffic_var[i]['timestamp'][:7] 
            if traffic_var[i]['timestamp'] == traffic_var[i+1]['timestamp'][:7]:
                traffic_var[i+1]['count'] +=  traffic_var[i]['count']
                traffic_var[i+1]['uniques'] +=  traffic_var[i]['uniques']
                remove_this.append(traffic_var[i])

        for item in remove_this:
            traffic_var.remove(item)

    return traffic_var

def dump_json(traffic, latest):
    with open(f'{traffic}.json', 'w', encoding='utf-8') as fh:
        json.dump(latest, fh, ensure_ascii=False, indent=4)

def run(traffic):
    now, before = load_json(traffic)
    timestamps = timestamp_list(traffic, before)
    latest = append_json(traffic, timestamps, before, now)
    latest = sum_counts(latest, traffic)
    traffic_var = latest[traffic]
    traffic_var = merge_counts(timestamps, traffic_var)
    traffic_var.sort(key=sort_key, reverse=True)
    dump_json(traffic, latest)

for traffic in ['clones', 'views']:
    run(traffic)
