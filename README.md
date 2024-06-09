This started as a fork of: [DotWiz by rnag](https://github.com/rnag/dotwiz)

# DotWiz

## "The blazing fast `dict` subclass that enables dot access notation via Python attribute style".

This was the tagline that caught my attention when I came across DotWiz recently. Python dictionaries are useful, but I've found myself creating classes in many cases where a simple dictionary would have sufficed, simply to take advantage of the dot syntax for attribute access. Dataclasses exist for this purpose, and I've used them from time to time. But Python's dictionaries do have some advantages of their own, so I was considering writing my own version of a dictionary wrapper similar to DotWiz when I discovered it. The original creator of Dotwiz claimed a 100x performance benefit for DotWiz vs Python's dataclasses, and perhaps that was true at the time, but it would seem that in 2024, dataclasses very handily outperformed it in most benchmarks.

## Can we fix it?

So, one weekend, having no life and therefore nothing better to do, I decided to take a deeper look into DotWiz and see if I could improve the performance in the most recent version of Python. (3.12.4 at the time of this writing).

## And??

Here's the TL:DR <i>(or rather TL:DW - for Too Lazy - Didn't Write)</i>

Benchmark results for dataset size 10000:
DotWiz creation: 0.0415 seconds
Original creation: 0.2996 seconds
Dataclass creation: 0.0140 seconds
DotWiz access: 0.0020 seconds
Original access: 0.0070 seconds
Dataclass access: 0.0000 seconds
DotWiz to dict: 0.0216 seconds
Original to dict: 0.4338 seconds
Dataclass to dict: 0.8838 seconds

```
Test 1: 10,000 objects with minimal nesting
    DotWiz (refactored)     |   DotWiz (original)   |   Dataclass
=========================== Instance Creation ==========================
    0.0415 seconds          |      0.2996 seconds    |   0.0140 seconds
=========================== Attribute access ===========================
    0.0020 seconds          |      0.0070 seconds    |   0.0000 seconds
=========================== Conversion to dict =========================
    0.0216 seconds          |      0.4338 seconds    |   0.8838 seconds

Test 2: 10,000 objects with heavily nested structure
=========================== Instance creation ===========================
    
=====================================================================
    0.0514 seconds          |                        |  0.0179 seconds

For one testing generating 10,000 objects, the updated version used 48.4MiB of RAM, while the original used 104MiB. Time to create the 10,000 instances was 0.0214 seconds for the updated version vs 0.2337 seconds for the original, an 89% advantage in this particular test. On the same data set in the same iteration of testing, Python native dataclasses used 127.6MiB of RAM,
and took 4.1489 seconds to complete the test. The dataset for this test case uses a heavily nested structure. It's noteworthy that on a much more simple dataset, the native dataclasses actually outperform the updated DotWiz class. For a data set with 10,000 objects generated, but very little nesting involved, DotWiz ran in 0.0514 seconds and native dataclasses ran in 0.0179 seconds. So YMMV depending on the structure of your data set. For the simpler data set, the updated DotWiz benchmarked for attribute access at 0.0020 to complete for 10,000 instances, against native dataclasses at 0.0010 seconds. Interestingly, on the more complex dataset, both classes completed in 0.0000 seconds. For cases where DotWiZ is faster, it seems to be MUCH faster than using dataclasses. For the cases where it's not, the difference is small enough to be considered negligible for most use cases. If performance is a concern, you have the option to disable the recursive conversion of objects stored within a DotWiz object's attributes. You can pass `_check_lists=False` to the constructor, and you can pass `_check_types=False`. The former disables the recursive conversion of lists, and the latter disables the recursive conversion of both lists and dicts. If you are not concerned about the internal objects also being converted to DotWiz instances, you can achieve significant performance gains this way, with the creation of 10,000 instances in the most complex test case registering only 0.0008 seconds, vs 0.1833 for the original and 4.1138 for native dataclasses, with memory usage for DotWiz remaining the same as before. DotWiz's to_dict method runs in 0.0320 seconds for 10,000 instance vs 0.9035 seconds for native dataclasses.
