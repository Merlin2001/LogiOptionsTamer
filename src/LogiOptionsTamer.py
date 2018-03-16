import datetime
import psutil
import sys
import time

# (Part of the) name of the process to keep tame
PROCESS_TO_KILL: str = "LogiOptionsMgr.exe"

# Kill process if it exceeds this cpu usage more than MAX_OVERRUN_COUNT times
CPU_USAGE_THRESHOLD_IN_PERCENT: float = 5

# Allow offending process to exceed usage threshold this many times
# (e.g. if set to 1 (default), the process can exceed the threshold one time.
#  If it still exceeds the threshold during the next check, it is restarted, if
#  not, the counter is reset.)
MAX_OVERRUN_COUNT: int = 1

# Wait this long between checks
SECONDS_BETWEEN_CHECKS: float = 60


# Switch debug output on/off
DEBUG_MODE: bool = False


def main():

    print("----- Running LogiOptionsTamer -----\n")
    overrunCount: int = 0

    # Run indefinitely
    while True:

        # Check if process with too high cpu usage is found
        # To-do: Define type for this variable (not possible at the moment,
        #        because typeshed doesn't contain psutil, yet)
        offender = getOffendingProcess()

        if offender is not None:
            overrunCount += 1
            user_log(f"Process exceeding cpu usage the {overrunCount}. time")
        else:
            overrunCount = 0    # Reset counter
            user_log("Process is tame :)")
        
        debug_log(f"overrunCount={overrunCount}")

        # If yes, kill process and restart it
        if overrunCount > MAX_OVERRUN_COUNT:
            restartProcess(offender)
            overrunCount = 0    # Reset counter

        # If no, just wait a minute :)
        debug_log("\n.,--zzZZ\n")
        time.sleep(SECONDS_BETWEEN_CHECKS)


# To-do: Define return type for this method (not possible at the moment, because
#        typeshed doesn't contain psutil, yet)
def getOffendingProcess():
    # Try to find process by name
    try:
        debug_log(f"Trying to get process by name '{PROCESS_TO_KILL}'")
        # To-do: Define type for this variable (not possible at the moment,
        #        because typeshed doesn't contain psutil, yet)
        firstPossibleOffender = [p for p in psutil.process_iter(attrs=['name']) 
                                        if PROCESS_TO_KILL in p.info['name']][0]
    except IndexError:
        user_log(f"Process '{PROCESS_TO_KILL}' not found...")
        return None

    # Note that psutil.cpu_percent reports the usage percent of the cpu core the
    # process is running on, so we have to divide it by the number of cores in 
    # the system to get a value that is similar to the Task Manager's
    cpuUsage: float = firstPossibleOffender.cpu_percent(interval=0.1) / psutil.cpu_count()

    if cpuUsage > CPU_USAGE_THRESHOLD_IN_PERCENT:
        debug_log(f"Process is behaving badly, using {cpuUsage}% CPU")
        return firstPossibleOffender
    else:
        debug_log(f"Process is tame, using {cpuUsage}% CPU")
        return None


def restartProcess(processToRestart):
    try:
        user_log(f"Restarting {processToRestart.name()}")

        # Ignore errors
        executablePath: str = processToRestart.cmdline()
        
        # Kill process
        processToRestart.kill()
        debug_log(f"{processToRestart.name()} killed - muhahahahaha.....")

        # Restart process
        psutil.Popen([executablePath])
        debug_log(f"Process restarted from: {executablePath}")
    
    except:
        print(f"Unexpected error: {sys.exc_info()[0]} - {sys.exc_info()[1]}")
        raise


# Logging methods
def debug_log(stringToLog: str):
    if DEBUG_MODE:
        print(f"{datetime.datetime.now()}: {stringToLog}")

def user_log(stringToLog: str):
    print(f"{datetime.datetime.now()}: {stringToLog}")


# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    main()
