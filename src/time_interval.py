from datetime import datetime, timedelta
import bisect

def print_intervals(intervals):
    if not intervals:
        print("No intervals stored.")
    else:
        print("Stored intervals:")
        for interval in intervals:
            print(f"From {interval[0]} to {interval[1]}")

def add_interval(intervals, start_date, end_date):
    # Insert the new interval while keeping the list sorted
    pos = bisect.bisect_right(intervals, [start_date, end_date])
    intervals.insert(pos, [start_date, end_date])
    
    # Merge any overlapping intervals
    merge_intervals(intervals)

def are_dates_adjacent(date1, date2):
    # Convert the string dates to datetime objects
    date1 = datetime.strptime(date1, "%d-%m-%Y")
    date2 = datetime.strptime(date2, "%d-%m-%Y")
    
    # Check if the difference between the two dates is exactly one day
    return abs((date2 - date1).days) == 1

def merge_intervals(intervals):
    merged = []
    for interval in intervals:
        if merged:
            date1End = datetime.strptime(merged[-1][1], "%d-%m-%Y")
        date2Start = datetime.strptime(interval[0], "%d-%m-%Y")
        date2End = datetime.strptime(interval[1], "%d-%m-%Y")
        if not merged or (date1End < date2Start and (not are_dates_adjacent(merged[-1][1], interval[0]))):
            merged.append(interval)
        else:
            newEndDate = max(date1End, date2End).strftime("%d-%m-%Y")
            merged[-1] = [merged[-1][0], newEndDate]
    intervals[:] = merged
