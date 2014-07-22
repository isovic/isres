#! /usr/bin/python

# (C) 2013, Ivan Sovic
#      ivan.sovic@gmail.com
#      http://www.sovic.org
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice, including the author's contact information
# and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Version v1.0, updated on: 2013/07/17, by Ivan Sovic.
#
#
# isRes is a tool for measuring time and memory statistics of a given process.

import subprocess
import threading
import time;
import sys;
import re;

VERBOSE_LEVEL_NONE = 0;
VERBOSE_LEVEL_LOW = 1;
VERBOSE_LEVEL_MEDIUM = 2;
VERBOSE_LEVEL_HIGH = 3;



# Convert various memory units to bytes.
def convertToBytes(value, unit):
	ret = value;
	
	if (unit=='k' or unit=='K'):
		ret *= 1024;
	elif (unit=='m' or unit=='M'):
		ret *= (1024 * 1024);
	elif (unit=='g' or unit=='G'):
		ret *= (1024 * 1024 * 1024);
	
	return ret;

# Convert bytes to various memory units.
def convertBytesToUnit(value, unit):
	ret = float(value);
	
	if (unit=='k' or unit=='K'):
		ret /= 1024;
	elif (unit=='m' or unit=='M'):
		ret /= (1024 * 1024);
	elif (unit=='g' or unit=='G'):
		ret /= (1024 * 1024 * 1024);
	
	return ret;

# Converts time from string format (consisting of ':' to separate hours, minutes and seconds) into a float representing the amount of seconds the given time contains.
def timeToSeconds(inTime):
	splitValues = inTime.split(':');
	power = 1.0;
	seconds = 0.0;
	
	for val in reversed(splitValues):
		tempSeconds = float(val) * power;
		power *= 60;
		seconds += tempSeconds;

	return seconds;

# Class to handle multithreading.
class myThread (threading.Thread):
	def __init__(self, threadID, name, commandLine):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.finished = 0;
		self.commandLine = commandLine;
		self.commandProcess = -1;
		self.commandProcessSet = 0;
		self.verbose = 0;
		self.outputTime = 'isRes-tempOutput.tme';
		self.outputMem = 'isRes-tempOutput.mem';
		self.executionTime = 0;
		
		self.peakValues = {};
		self.resetPeakValues();
		
	def run(self):
		self.finished = 0;
		
		if (self.verbose >= VERBOSE_LEVEL_LOW):
			print 'isRes: Running process "' + self.name + '"...\n'
		
		self.runProgram();
		
		if (self.verbose >= VERBOSE_LEVEL_LOW):
			print 'isRes: Process "' + self.name + '" completed.';
		
		self.finished = 1;
	
	def resetPeakValues(self):
		self.peakValues['Rss'] = 0;
		self.peakValues['Pss'] = 0;
		self.peakValues['VmSize'] = 0;
		self.peakValues['realTime'] = 0.0;
		self.peakValues['cpuTime'] = 0.0;
	
	# Runs the given command.
	def runProgram(self):
		newCommand = r'/usr/bin/time -f "isRes: %E elapsed, %U user, %S system, %P CPU" --output=' + str(self.outputTime) + ' ' + self.commandLine;

		self.resetPeakValues();

		self.commandProcess = subprocess.Popen(newCommand, shell=True);
		self.commandProcessSet = 1;
		self.commandProcess.wait();
		self.commandProcessSet = 0;
	
	# Parses system files to retreive memory information for the running process. Parameter units is used only for display purposes, the values are always returned in bytes. Parameter separator is used for outputing memory statistics to a file. If self.outputMem == '', then the memory statistics will not be written to file.
	def getMemoryInfo(self, units='B', separator=','):
		if (self.commandProcessSet == 0):
			return;
		
		units = str(units);
		separator = str(separator);
		
		pid = self.commandProcess.pid;
		pidChildren = self.getPidChildren(pid);
		
		rootStatusData = self.getProcStatusData(pid);
		rootSmapsData = self.getProcSmapsData(pid);
		
		ret = {};
		for key in self.peakValues.keys():
			ret[key] = 0;
		
		if (self.verbose >= VERBOSE_LEVEL_MEDIUM):
			print 'Root process PID:  %s,\tRSS: %s %sB,\tPSS: %s %sB,\tVmSize: %s %sB' % (str(pid), str(convertBytesToUnit(int(rootSmapsData['Rss']), units)), units, str(convertBytesToUnit(int(rootSmapsData['Pss']), units)), units, str(convertBytesToUnit(int(rootStatusData['VmSize']), units)), units);
		
		for key in ret.keys():
			try:
				valueStatusData = rootStatusData[key];
			except:
				valueStatusData = 0;
			
			try:
				valueSmapsData = rootSmapsData[key];
			except:
				valueSmapsData = 0;

			ret[key] += valueStatusData + valueSmapsData;
			
		for childPid in pidChildren:
			statusData = self.getProcStatusData(childPid);
			smapsData = self.getProcSmapsData(childPid);
			
			if (self.verbose >= VERBOSE_LEVEL_MEDIUM):
				print 'Child process PID: %s,\tRSS: %s %sB,\tPSS: %s %sB,\tVmSize: %s %sB' % (str(childPid), str(convertBytesToUnit(int(smapsData['Rss']), units)), units, str(convertBytesToUnit(int(smapsData['Pss']), units)), units, str(convertBytesToUnit(int(statusData['VmSize']), units)), units);
			
			for key in ret.keys():
				try:
					valueStatusData = statusData[key];
				except:
					valueStatusData = 0;
				
				try:
					valueSmapsData = smapsData[key];
				except:
					valueSmapsData = 0;

				ret[key] += valueStatusData + valueSmapsData;
		
		for key in ret.keys():
			if (self.peakValues[key] < ret[key]):
				self.peakValues[key] = ret[key];
		
		if (self.verbose >= VERBOSE_LEVEL_MEDIUM):
			print 'Current sum => RSS: %s %sB,\tPSS: %s %sB,\tVmSize: %s %sB' % (str(convertBytesToUnit(int(ret['Rss']), units)), units, str(convertBytesToUnit(int(ret['Pss']), units)), units, str(convertBytesToUnit(int(ret['VmSize']), units)), units);

		if (self.verbose >= VERBOSE_LEVEL_MEDIUM):
			print 'Peak values => RSS: %s %sB,\tPSS: %s %sB,\tVmSize: %s %sB' % (str(convertBytesToUnit(int(self.peakValues['Rss']), units)), units, str(convertBytesToUnit(int(self.peakValues['Pss']), units)), units, str(convertBytesToUnit(int(self.peakValues['VmSize']), units)), units);
		
		if (self.verbose >= VERBOSE_LEVEL_MEDIUM):
			print ' ';
		
		if (len(self.outputMem) > 0):
			try:
				f = open(self.outputMem, 'a');
				
				line =	'realTime=' + str(self.executionTime) + 's' + separator + 'RSS=' + str(convertBytesToUnit(int(self.peakValues['Rss']), units)) + units + 'B' + separator + \
						'PSS=' + str(convertBytesToUnit(int(self.peakValues['Pss']), units)) + units + 'B' + separator + \
						'VmSize=' + str(convertBytesToUnit(int(self.peakValues['VmSize']), units)) + units + 'B';
				
				f.write(line + '\n');
				
				f.close();
			except IOError:
				if (self.verbose >= VERBOSE_LEVEL_LOW):
					print '\t> ERROR: File "%s" not found!' % self.outputMem
		
		

		return ret;
	
	# Gets a list of child PIDs from a process tree for a given process (also through pid).
	def getPidChildren(self, pid):
		ret = [];
		
		pipe = subprocess.Popen('/usr/bin/pstree -c -p ' + str(pid), shell=True, stdout=subprocess.PIPE)
		# communicate() returns a tuple (stdoutdata, stderrdata)
		processes = pipe.communicate()[0]
		
		matchObj = re.findall(r'\((\d+)\)', processes);
		
		matchObj = [element for element in matchObj if element != str(pid)]
		
		return matchObj;
	
	# Gets data from the /proc/pid/status file.
	def getProcStatusData(self, pid):
		ret = {};
		
		inFile = r'/proc/' + str(pid) + r'/status';
		
		try:
			with open(inFile) as f:
				for line in f:
					line = line.rstrip();
					splitLine = line.split(':');
					
					if (len(splitLine) != 2):
						continue;
					
					paramName = splitLine[0].strip();
					paramValue = splitLine[1].strip();
					
					matchObj = re.match(r'\s*(\d+)\s*(.?)B', paramValue);
					
					if (matchObj):
						paramValueBytes = int(convertToBytes(int(matchObj.group(1)), matchObj.group(2)));
						
						ret[paramName] = paramValueBytes;
					
		except IOError:
			if (self.verbose >= VERBOSE_LEVEL_HIGH):
				print '\t> ERROR: File "%s" not found in function getProcStatusData(...)!' % inFile
				
			pass;
			
		return ret;
	
	# Gets data from the /proc/pid/smaps file.
	def getProcSmapsData(self, pid):
		ret = {};
		
		inFile = r'/proc/' + str(pid) + r'/smaps';
		
		try:
			with open(inFile) as f:
				for line in f:
					line = line.rstrip();
					splitLine = line.split(':');
					
					if (len(splitLine) != 2):
						continue;
					
					paramName = splitLine[0].strip();
					paramValue = splitLine[1].strip();
					

					matchObj = re.match(r'\s*(\d+)\s*(.?)B', paramValue);
					
					if (matchObj):
						paramValueBytes = int(convertToBytes(int(matchObj.group(1)), matchObj.group(2)));
						
						try:
							ret[paramName] += paramValueBytes;
						except:
							ret[paramName] = paramValueBytes;
					
		except IOError:
			if (self.verbose >= VERBOSE_LEVEL_HIGH):
				print '\t> ERROR: File "%s" not found in function getProcSmapsData(...)!' % inFile
				
			pass;
			
		return ret;
	
	# Parses the time measurements (obtained with /usr/bin/time and output to a file).
	def parseTimeMeasurements(self):
		try:
			with open(self.outputTime) as f:
				for line in f:
				
					matchObj = re.match(r'isRes: (.*) elapsed, (.*) user, (.*) system, (.*) CPU', line, re.M|re.I);
					
					if matchObj:
						realTime = timeToSeconds(matchObj.group(1));
						userTime = timeToSeconds(matchObj.group(2));
						systemTime = timeToSeconds(matchObj.group(3));
						cpuTime = userTime + systemTime;

						if (self.verbose >= VERBOSE_LEVEL_MEDIUM):
							print 'realTime: %f, cpuTime: %f, userTime: %f, systemTime: %f' % (realTime, cpuTime, userTime, systemTime);

						self.peakValues['realTime'] = realTime;
						self.peakValues['cpuTime'] = cpuTime;
						
						break;
				
		except IOError:
			if (self.verbose >= VERBOSE_LEVEL_LOW):
				print '\t> ERROR: File "%s" not found!' % measureFilePath
	
	# Formats the output of the measurement process in form of text.
	def summaryText(self, memoryUnits, adj, separator):
		ret =	'realTime' + adj + str(self.peakValues['realTime']) + ' s' + separator + \
				'cpuTime' + adj + str(self.peakValues['cpuTime']) + ' s' + separator + \
				'memRSS' + adj + str(convertBytesToUnit(int(self.peakValues['Rss']), memoryUnits)) + ' ' + str(memoryUnits) + 'B' + separator + \
				'memPSS' + adj + str(convertBytesToUnit(int(self.peakValues['Pss']), memoryUnits)) + ' ' + str(memoryUnits) + 'B' + separator + \
				'memVmSize' + adj + str(convertBytesToUnit(int(self.peakValues['VmSize']), memoryUnits)) + ' ' + str(memoryUnits) + 'B';

		return ret;
		
	# Formats the output of the measurement process in form of a list.
	def summary(self, memoryUnits):
		ret =	[float(self.peakValues['realTime']), float(self.peakValues['cpuTime']),  float(convertBytesToUnit(int(self.peakValues['Rss']), memoryUnits)), float(convertBytesToUnit(int(self.peakValues['Pss']), memoryUnits)), float(convertBytesToUnit(int(self.peakValues['VmSize']), memoryUnits))];

		return ret;

# Runs the measurement process.
def measure(commandLine, outputTime, outputMem, outputSum, memoryUnits, verbose, samplePeriod):
	samplePeriod = int(samplePeriod);
	
	threadProgram = myThread(1, 'executionThread', commandLine);
	
	threadProgram.verbose = verbose;
	threadProgram.outputTime = outputTime;
	threadProgram.outputMem = outputMem;
	threadProgram.executionTime = 0;
	
	if (len(outputMem) > 0):
		try:
			f = open(threadProgram.outputMem, 'w');
			f.close();
		except IOError:
			if (threadProgram.verbose >= VERBOSE_LEVEL_LOW):
				print '\t> ERROR: File "%s" not found!' % threadProgram.outputMem;
	
	threadProgram.start();

	while(threadProgram.finished == 0):
		if (threadProgram.commandProcessSet == 1):
			threadProgram.executionTime += 1;
			threadProgram.getMemoryInfo(memoryUnits);
		
		time.sleep(samplePeriod);
	
	threadProgram.parseTimeMeasurements();

	summaryLine = threadProgram.summaryText(memoryUnits, ' =\t', '\n\t');
	try:
		fp_sum = open(outputSum, 'w');
		fp_sum.write('Summary:\n\t%s\n' % summaryLine);
		fp_sum.close();
	except IOError:
		if (threadProgram.verbose >= VERBOSE_LEVEL_LOW):
			print 'ERROR: Summary file could not be created!';

	if (threadProgram.verbose >= VERBOSE_LEVEL_LOW):
#		print 'Summary:\n\t%s' % threadProgram.summaryText(memoryUnits, ' =\t', '\n\t');
		print 'Summary:\n\t%s' % summaryLine;

		print "isRes: Measurement completed."
	
	return threadProgram.summary(memoryUnits);
	
def main():
	verboseLevel = VERBOSE_LEVEL_NONE;
	samplePeriod = 1;			# Memory sampling period, in seconds.

	if (len(sys.argv) < 4):
		print 'Usage:';
		print '\t' + sys.argv[0] + ' OUTPUT_PREFIX MEMORY_UNIT COMMAND [PARAMETERS]';
		print ' ';
		print '\tOUTPUT_PREFIX\t- prefix for the output files. Three files will be generated: OUTPUT_PREFIX.tme, OUTPUT_PREFIX.mem and OUTPUT_PREFIX.sum .';
		print '\tMEMORY_UNIT\t- memory measurements can be output in bytes (B), kilobytes (k), megabytes (M) or gigabytes (G). This parameter should be set to one of: B, k, M, G.'
		print '\tCOMMAND [PARAMETERS]\t- Bash command (with corresponding parameters) that will be executed and monitored.';
		exit(1);
	
	memoryUnit = sys.argv[2];
	if (memoryUnit == 'B'):
		memoryUnit = '';
		
	commandWithParameters = ' '.join(sys.argv[3:]);
	measure(commandWithParameters, sys.argv[1] + '.tme', sys.argv[1] + '.mem', sys.argv[1] + '.sum', memoryUnit, verboseLevel, samplePeriod);

if __name__ == "__main__":
   main()
