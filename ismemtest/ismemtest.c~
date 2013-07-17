#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>



unsigned long long getCurrentMillis()
{
    struct timeval currentTime;
    long mtime, seconds, useconds;
	
    gettimeofday(&currentTime, NULL);

    seconds  = currentTime.tv_sec;
    useconds = currentTime.tv_usec;

    mtime = ((seconds) * 1000 + useconds/1000.0);
	
	return mtime;
}

int main(int argc, char *argv[])
{
	if (argc < 3)
	{
		printf ("Usage:\t%s <number_of_megabytes_to_allocate> <amount_of_milliseconds_to_sleep>\n", argv[0]);
		return 1;
	}
	
	char *allocatedMemory=NULL;
	unsigned long long int i=0;
	unsigned long long int memSize=1048576;
	memSize *= atoi(argv[1]);
	unsigned long long int wait=atoi(argv[2]);
	unsigned long  long startMillis=0;
	
	startMillis = getCurrentMillis();

	allocatedMemory = (char *) calloc(sizeof(char), memSize);
	
	while ((getCurrentMillis()-startMillis) < wait);

	if (allocatedMemory)
		free(allocatedMemory);

	printf ("Memtest done. Allocated %lld bytes (%.4lfkB, %.4lfMB, %.4lfGB) of memory.\n", memSize, ((double) memSize)/(1024.0f), ((double) memSize)/(1024.0f*1024.0f), ((double) memSize)/(1024.0f*1024.0f*1024.0f));

	return 0;
}
