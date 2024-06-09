This started as a fork of: [DotWiz by rnag](https://github.com/rnag/dotwiz)

# DotWiz

## "The blazing fast `dict` subclass that enables dot access notation via Python attribute style".

This was the tagline that caught my attention when I came across DotWiz recently. Python dictionaries are useful, but I've found myself creating classes in many cases where a simple dictionary would have sufficed, simply to take advantage of the dot syntax for attribute access. Dataclasses exist for this purpose, and I've used them from time to time. But Python's dictionaries do have some advantages of their own, so I was considering writing my own version of a dictionary wrapper similar to DotWiz when I discovered it. The original creator of Dotwiz claimed a 100x performance benefit for DotWiz vs Python's dataclasses, and perhaps that was true at the time, but it would seem that in 2024, dataclasses very handily outperformed it in most benchmarks.

## Can we fix it?

So, one weekend, having no life and therefore nothing better to do, I decided to take a deeper look into DotWiz and see if I could improve the performance in the most recent version of Python. (3.12.4 at the time of this writing).

## And??

Here's the TL:DR <i>(or rather TL:DW - for Too Lazy - Didn't Write)</i>

The refactored DotWiz is significantly improved over the original in terms of both speed and memory usage, but both are vastly outperformed by dataclasses in the time required to create an instance.  Attribute access time is basically negligible for all three data structures.  The refactored DotWiz is a clear winner when converting objects to native Python dictionaries, so it's worth a look if that's your use case.   

```
Test 1: 10,000 objects with minimal nesting
    DotWiz (refactored)     |   DotWiz (original)     |   Dataclass        
=========================== Instance Creation =================================   
    0.1679 seconds  3.6MiB  |   0.4414 seconds 57.8MiB|   0.0161 seconds 0.1MiB
=========================== Attribute access ==================================
    0.0040 seconds          |   0.0090 seconds        |   0.0064 seconds
=========================== Conversion to dict ================================
    0.0202 seconds  3.6MiB  |   0.4602 seconds 77.9MiB|   1.0181 seconds 132.4MiB

Test 2: 10,000 objects with heavily nested structure
=========================== Instance creation ===========================
    0.1250 seconds          |      0.1613 seconds    |   0.0084 seconds    
=========================== Attribute access ============================
    0.0000 seconds          |      0.0157 seconds    |   0.0021 seconds
=========================== Conversion to dict ==========================
    0.0156 seconds          |      0.1719 seconds    |   0.4769 seconds
```