# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")

def solution(E):
    # Implement your solution here
    max_attendance = 0
    days = range(10)  # Days are represented as 0 to 9

    # Check all combinations of two days
    for day1 in days:
        for day2 in days:
            if day1 != day2:  # Ensure we are checking two different days
                attendance = 0
                for employee in E:
                    # Check if the employee is available on either day
                    if str(day1) in employee or str(day2) in employee:
                        attendance += 1
                max_attendance = max(max_attendance, attendance)

    return max_attendance