import time
from CNC600.pulse.dotwiz import DotWiz
from dotwiz import DotWiz as DotWizOriginal
from memory_profiler import profile
from dataclasses import make_dataclass
def create_large_dataset(size):
    return [
        {
            "key1": "value1",
            "key2": [{"nested_key1": "nested_value1", "nested_key2": i} for i in range(10)],
            "key3": 3.21,
        }
        for _ in range(size)
    ]

@profile
def benchmark_dotwiz(data):
    start = time.time()
    dotwiz_instances = [DotWiz(item, _check_lists=False, _check_types=False) for item in data]
    end = time.time()
    return end - start

def benchmark_original(data):
    start = time.time()
    original_instances = [DotWizOriginal(item) for item in data]
    end = time.time()
    return end - start

def benchmark_dataclass(data):
    start = time.time()
    dataclass_instances = [make_dataclass("DataClassExample", item.keys())(**item) for item in data]
    end = time.time()
    return end - start

@profile
def benchmark_access(instance_list):
    start = time.time()
    for instance in instance_list:
        _ = instance.key1
        _ = instance.key2[0]["nested_key1"]
        _ = instance.key3
    end = time.time()
    return end - start


# Create dataset
dataset_size = 10000
data = create_large_dataset(dataset_size)

# Perform benchmarks
dotwiz_time = benchmark_dotwiz(data)
original_time = benchmark_original(data)
dataclass_time = benchmark_dataclass(data)
dotwiz_instances = [DotWiz(item, _check_lists=False) for item in data]
dotwiz_access_time = benchmark_access(dotwiz_instances)
original_instances = [DotWizOriginal(item) for item in data]
original_access_time = benchmark_access(original_instances)
dataclass_instances = [make_dataclass("DataClassExample", item.keys())(**item) for item in data]
dataclass_access_time = benchmark_access(dataclass_instances)

# Print results
print(f"DotWiz creation: {dotwiz_time:.4f} seconds")
print(f"Original creation: {original_time:.4f} seconds")
print(f"Dataclass creation: {dataclass_time:.4f} seconds")
print(f"DotWiz access: {dotwiz_access_time:.4f} seconds")
print(f"Original access: {original_access_time:.4f} seconds")
print(f"Dataclass access: {dataclass_access_time:.4f} seconds")
