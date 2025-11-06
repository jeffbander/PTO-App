"""
Business Days Calculator for PTO System
Excludes weekends and federal holidays from PTO calculations
"""

from datetime import datetime, date, timedelta
from typing import List, Set


class BusinessDaysCalculator:
    """Calculate business days excluding weekends and federal holidays"""

    @staticmethod
    def get_federal_holidays(year: int) -> Set[date]:
        """
        Get federal holidays for a given year
        Returns a set of date objects for major US federal holidays
        """
        holidays = set()

        # New Year's Day - January 1
        holidays.add(date(year, 1, 1))

        # Martin Luther King Jr. Day - Third Monday in January
        jan_first = date(year, 1, 1)
        days_to_first_monday = (7 - jan_first.weekday()) % 7
        first_monday = jan_first + timedelta(days=days_to_first_monday)
        mlk_day = first_monday + timedelta(days=14)  # Third Monday
        holidays.add(mlk_day)

        # Presidents' Day - Third Monday in February
        feb_first = date(year, 2, 1)
        days_to_first_monday = (7 - feb_first.weekday()) % 7
        first_monday = feb_first + timedelta(days=days_to_first_monday)
        presidents_day = first_monday + timedelta(days=14)  # Third Monday
        holidays.add(presidents_day)

        # Memorial Day - Last Monday in May
        may_31 = date(year, 5, 31)
        days_back_to_monday = (may_31.weekday() - 0) % 7
        memorial_day = may_31 - timedelta(days=days_back_to_monday)
        holidays.add(memorial_day)

        # Independence Day - July 4
        holidays.add(date(year, 7, 4))

        # Labor Day - First Monday in September
        sep_first = date(year, 9, 1)
        days_to_first_monday = (7 - sep_first.weekday()) % 7
        labor_day = sep_first + timedelta(days=days_to_first_monday)
        holidays.add(labor_day)

        # Columbus Day - Second Monday in October
        oct_first = date(year, 10, 1)
        days_to_first_monday = (7 - oct_first.weekday()) % 7
        first_monday = oct_first + timedelta(days=days_to_first_monday)
        columbus_day = first_monday + timedelta(days=7)  # Second Monday
        holidays.add(columbus_day)

        # Veterans Day - November 11
        holidays.add(date(year, 11, 11))

        # Thanksgiving - Fourth Thursday in November
        nov_first = date(year, 11, 1)
        days_to_first_thursday = (3 - nov_first.weekday()) % 7
        first_thursday = nov_first + timedelta(days=days_to_first_thursday)
        thanksgiving = first_thursday + timedelta(days=21)  # Fourth Thursday
        holidays.add(thanksgiving)

        # Christmas Day - December 25
        holidays.add(date(year, 12, 25))

        return holidays

    @staticmethod
    def is_business_day(check_date: date) -> bool:
        """
        Check if a given date is a business day
        Returns False for weekends and federal holidays
        """
        # Check if it's a weekend (Saturday=5, Sunday=6)
        if check_date.weekday() >= 5:
            return False

        # Check if it's a federal holiday
        year_holidays = BusinessDaysCalculator.get_federal_holidays(check_date.year)
        if check_date in year_holidays:
            return False

        return True

    @staticmethod
    def calculate_business_days(start_date: date, end_date: date) -> int:
        """
        Calculate the number of business days between two dates (inclusive)
        Excludes weekends and federal holidays
        """
        if start_date > end_date:
            return 0

        business_days = 0
        current_date = start_date

        while current_date <= end_date:
            if BusinessDaysCalculator.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)

        return business_days

    @staticmethod
    def get_business_days_list(start_date: date, end_date: date) -> List[date]:
        """
        Get a list of all business days between two dates (inclusive)
        Excludes weekends and federal holidays
        """
        business_days = []
        current_date = start_date

        while current_date <= end_date:
            if BusinessDaysCalculator.is_business_day(current_date):
                business_days.append(current_date)
            current_date += timedelta(days=1)

        return business_days

    @staticmethod
    def get_holiday_info(start_date: date, end_date: date) -> dict:
        """
        Get detailed information about holidays and weekends in a date range
        Returns breakdown of total days, business days, weekends, and holidays
        """
        if start_date > end_date:
            return {
                'total_days': 0,
                'business_days': 0,
                'weekend_days': 0,
                'holiday_days': 0,
                'holidays_list': [],
                'weekends_list': []
            }

        total_days = (end_date - start_date).days + 1
        business_days = 0
        weekend_days = 0
        holiday_days = 0
        holidays_list = []
        weekends_list = []

        # Get all holidays for the years involved
        years = set()
        current_date = start_date
        while current_date <= end_date:
            years.add(current_date.year)
            current_date += timedelta(days=1)

        all_holidays = set()
        for year in years:
            all_holidays.update(BusinessDaysCalculator.get_federal_holidays(year))

        # Count each type of day
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() >= 5:  # Weekend
                weekend_days += 1
                weekends_list.append(current_date)
            elif current_date in all_holidays:  # Holiday
                holiday_days += 1
                holidays_list.append(current_date)
            else:  # Business day
                business_days += 1

            current_date += timedelta(days=1)

        return {
            'total_days': total_days,
            'business_days': business_days,
            'weekend_days': weekend_days,
            'holiday_days': holiday_days,
            'holidays_list': holidays_list,
            'weekends_list': weekends_list
        }


# Convenience functions for easy import
def calculate_pto_days(start_date_str: str, end_date_str: str) -> int:
    """
    Calculate PTO days (business days only) from date strings
    Format: 'YYYY-MM-DD'
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        return BusinessDaysCalculator.calculate_business_days(start_date, end_date)
    except ValueError:
        return 0


def get_pto_breakdown(start_date_str: str, end_date_str: str) -> dict:
    """
    Get detailed breakdown of PTO request including holidays and weekends
    Format: 'YYYY-MM-DD'
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        return BusinessDaysCalculator.get_holiday_info(start_date, end_date)
    except ValueError:
        return {
            'total_days': 0,
            'business_days': 0,
            'weekend_days': 0,
            'holiday_days': 0,
            'holidays_list': [],
            'weekends_list': []
        }


if __name__ == "__main__":
    # Test the calculator
    print("Business Days Calculator Test")
    print("=" * 40)

    # Test case: Thursday to Tuesday (should exclude weekend)
    start = date(2025, 12, 18)  # Thursday
    end = date(2025, 12, 23)    # Tuesday

    info = BusinessDaysCalculator.get_holiday_info(start, end)
    print(f"Dec 18-23, 2025 (Thu-Tue):")
    print(f"  Total days: {info['total_days']}")
    print(f"  Business days: {info['business_days']}")
    print(f"  Weekend days: {info['weekend_days']}")
    print(f"  Holiday days: {info['holiday_days']}")

    # Test case: Including Christmas
    start = date(2025, 12, 24)  # Wednesday
    end = date(2025, 12, 26)    # Friday

    info = BusinessDaysCalculator.get_holiday_info(start, end)
    print(f"\nDec 24-26, 2025 (Wed-Fri, includes Christmas):")
    print(f"  Total days: {info['total_days']}")
    print(f"  Business days: {info['business_days']}")
    print(f"  Weekend days: {info['weekend_days']}")
    print(f"  Holiday days: {info['holiday_days']}")
    print(f"  Holidays: {[h.strftime('%m/%d') for h in info['holidays_list']]}")