isres
=====

isRes is a simple Python script for measuring resource consumption on Linux platforms.
It can be used as a standalone script, or imported into another Python module.

isRes measures the following statistics:
1. Real time - time that a process took to execute.
2. CPU time - time that the CPU spent processing a given process. (It is equal to user time + system time)
3. RSS (Resident Set Size) - total amount of RAM that the process occupied.
4. PSS (Proportional Set Size) - amount of RAM that the process occupied, but with respect to shared libraries.
5. VmSize - Size of the virtual memory requested by the process.

These statistics are derived from:
- Real time and CPU time - obtained using the /usr/bin/time tool.
- RSS and PSS - obtained from /proc/pid/smaps system file.
- VmSize - obtained from /proc/pid/status system file.

isRes script outputs time and memory measurements into two separate output files (outputPrefix.tme and outputPrefix.mem). Currently, the outputPrefix.tme is necessary, but outputPrefix.mem can be omitted (by setting outputMem = ''; check the comments in isRes.py).

Memory measurements are performed periodically on a given timely basis (in seconds). They are written to file purely for backup purposes (in case your process crashes).

Additionally, a simple benchmarking tool (ismemtest) has been created. This is nothing more than a C program that allocates the desired amount of memory in MB, and runs for a specified amount of milliseconds.



Example usage:
	./isres.py outputPrefix grep -r txt ~/			# Be careful running this, it may take a while :)

More example cases can be found in the examples/folder.



Written by Ivan Sović, 2013.
