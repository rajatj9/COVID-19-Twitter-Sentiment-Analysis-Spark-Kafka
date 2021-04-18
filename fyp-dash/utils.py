from functools import reduce
from config import MAX_SIZE
from collections import Counter
from datetime import datetime

def get_new_data_dict(consumer) -> Counter:
    new_data = consumer.poll(max_records=MAX_SIZE)
    new_data_array = []
    for tp in new_data:
        records = new_data[tp]
        if not records:
            continue
        print(records)
        records = map(lambda x: x.value['data'], records)  # List of list of tuples
        record_dicts = [Counter(dict(record)) for record in records]
        new_data_array = new_data_array + record_dicts
    # print("Newly Fetched Data: ", new_data_array)
    return reduce(lambda a, b: a + b, new_data_array) if new_data_array else Counter({})


def get_updated_cache_value(consumer, cache, cache_key, max_size):
    start = datetime.now()
    new_data = get_new_data_dict(consumer)
    end = datetime.now()
    print(f"Time for creating dict from new records for {cache_key}:", end - start)
    updated_data = new_data + Counter(cache[cache_key])
    print("Time for adding new records: ")
    sorted_data = sorted(updated_data.items(), key=lambda x: x[1], reverse=True)
    print(f"Time for sorting records for {cache_key}: ", datetime.now() - end)
    return dict(sorted_data[:max_size])
