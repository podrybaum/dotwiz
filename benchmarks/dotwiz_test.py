import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from CNC600.pulse.dotwiz import DotWiz


# Dataclass implementation
@dataclass
class DataClassExample:
    key1: str
    key2: List[Dict[str, Any]]
    key3: float


# Function to create a large dataset of dictionaries
def create_large_dataset(size):
    return [
        {
            "key1": "value1",
            "key2": [{"nested_key1": "nested_value1", "nested_key2": i} for i in range(10)],
            "key3": 3.21,
        }
        for _ in range(size)
    ]


# Function to benchmark DotWiz
def benchmark_dotwiz(data):
    start = time.time()
    dotwiz_instances = [DotWiz(item) for item in data]
    end = time.time()
    return end - start


    return end - start


# Function to benchmark dataclasses
def benchmark_dataclass(data):
    start = time.time()
    dataclass_instances = [DataClassExample(**item) for item in data]
    end = time.time()
    return end - start


# Function to benchmark access time
def benchmark_access(instance_list):
    start = time.time()
    for instance in instance_list:
        _ = instance.key1
        _ = instance.key2[0]["nested_key1"]
        _ = instance.key3
    end = time.time()
    return end - start


# Function to benchmark dataclass conversion to dict
def benchmark_dataclass_to_dict(data):
    start = time.time()
    dataclass_dicts = [asdict(DataClassExample(**item)) for item in data]
    end = time.time()
    return end - start


def benchmark_dotwiz_to_dict(data):
    dotwiz_dicts = [DotWiz(d) for d in data]
    start = time.time()
    out_dicts = [DotWiz.to_dict(dw) for dw in dotwiz_dicts]
    end = time.time()
    return end - start


# Benchmark sizes
dataset_size = 10000  # Adjust size as needed
data = create_large_dataset(dataset_size)


import cProfile
import pstats
from io import StringIO


# Function to run the benchmark
def run_benchmark():
    dotwiz_time = benchmark_dotwiz(data)
   
    dataclass_time = benchmark_dataclass(data)
    dotwiz_instances = [DotWiz(item) for item in data]

    dataclass_instances = [DataClassExample(**item) for item in data]
    dotwiz_access_time = benchmark_access(dotwiz_instances)
    dotwiz_to_dict_time = benchmark_dotwiz_to_dict(data)
    dataclass_access_time = benchmark_access(dataclass_instances)
    dataclass_to_dict_time = benchmark_dataclass_to_dict(data)
    print(f"Benchmark results for dataset size {dataset_size}:")
    print(f"DotWiz creation: {dotwiz_time:.4f} seconds")

    print(f"Dataclass creation: {dataclass_time:.4f} seconds")
    print(f"DotWiz access: {dotwiz_access_time:.4f} seconds")

    print(f"Dataclass access: {dataclass_access_time:.4f} seconds")
    print(f"Dataclass to dict: {dataclass_to_dict_time:.4f} seconds")
    print(f"DotWiz to dict: {dotwiz_to_dict_time:.4f} seconds")

# Profile the benchmark
pr = cProfile.Profile()
pr.enable()
run_benchmark()
pr.disable()

# Print profiling results
s = StringIO()
sortby = "cumulative"
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
