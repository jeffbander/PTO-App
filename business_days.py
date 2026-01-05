"""
Business Days Calculator for PTO System
Excludes weekends and Mount Sinai official holidays from PTO calculations
"""

from datetime import datetime, date, timedelta
from typing import List, Set, Dict


class BusinessDaysCalculator:
    """Calculate business days excluding weekends and Mount Sinai holidays"""

    # Mount Sinai Official Holidays
    HOLIDAY_NAMES = {
        'new_years': "New Year's Day",
        'mlk': 'Martin Luther King Jr. Day',
        'presidents': "Presidents' Day",
        'memorial': 'Memorial Day',
        'juneteenth': 'Juneteenth',
        'independence': 'Independence Day',
        'labor': 'Labor Day',
        'thanksgiving': 'Thanksgiving',
        'christmas': 'Christmas Day'
    }

    @staticmethod
    def get_observed_date(holiday_date: date) -> date:
        """
        Get the observed date for a holiday.
        If holiday falls on Saturday, observed on Friday.
        If holiday falls on Sunday, observed on Monday.
        """
        if holiday_date.weekday() == 5:  # Saturday
            return holiday_date - timedelta(days=1)  # Observe on Friday
        elif holiday_date.weekday() == 6:  # Sunday
            return holiday_date + timedelta(days=1)  # Observe on Monday
        return holiday_date

    @staticmethod
    def get_mount_sinai_holidays(year: int) -> Set[date]:
        """
        Get Mount Sinai official holidays for a given year
        Returns a set of date objects for the 9 official holidays
        """
        holidays = set()

        # New Year's Day - January 1 (observed if on weekend)
        new_years = date(year, 1, 1)
        holidays.add(BusinessDaysCalculator.get_observed_date(new_years))

        # Martin Luther King Jr. Day - Third Monday in January
        jan_first = date(year, 1, 1)
        days_to_first_monday = (7 - jan_first.weekday()) % 7
        if jan_first.weekday() == 0:  # If Jan 1 is Monday
            days_to_first_monday = 0
        first_monday = jan_first + timedelta(days=days_to_first_monday)
        mlk_day = first_monday + timedelta(days=14)  # Third Monday
        holidays.add(mlk_day)

        # Presidents' Day - Third Monday in February
        feb_first = date(year, 2, 1)
        days_to_first_monday = (7 - feb_first.weekday()) % 7
        if feb_first.weekday() == 0:  # If Feb 1 is Monday
            days_to_first_monday = 0
        first_monday = feb_first + timedelta(days=days_to_first_monday)
        presidents_day = first_monday + timedelta(days=14)  # Third Monday
        holidays.add(presidents_day)

        # Memorial Day - Last Monday in May
        may_31 = date(year, 5, 31)
        days_back_to_monday = (may_31.weekday() - 0) % 7
        memorial_day = may_31 - timedelta(days=days_back_to_monday)
        holidays.add(memorial_day)

        # Juneteenth - June 19 (observed if on weekend)
        juneteenth = date(year, 6, 19)
        holidays.add(BusinessDaysCalculator.get_observed_date(juneteenth))

        # Independence Day - July 4 (observed if on weekend)
        independence_day = date(year, 7, 4)
        holidays.add(BusinessDaysCalculator.get_observed_date(independence_day))

        # Labor Day - First Monday in September
        sep_first = date(year, 9, 1)
        days_to_first_monday = (7 - sep_first.weekday()) % 7
        if sep_first.weekday() == 0:  # If Sep 1 is Monday
            days_to_first_monday = 0
        labor_day = sep_first + timedelta(days=days_to_first_monday)
        holidays.add(labor_day)

        # Thanksgiving - Fourth Thursday in November
        nov_first = date(year, 11, 1)
        days_to_first_thursday = (3 - nov_first.weekday()) % 7
        if nov_first.weekday() == 3:  # If Nov 1 is Thursday
            days_to_first_thursday = 0
        first_thursday = nov_first + timedelta(days=days_to_first_thursday)
        thanksgiving = first_thursday + timedelta(days=21)  # Fourth Thursday
        holidays.add(thanksgiving)

        # Christmas Day - December 25 (observed if on weekend)
        christmas = date(year, 12, 25)
        holidays.add(BusinessDaysCalculator.get_observed_date(christmas))

        return holidays

    @staticmethod
    def get_mount_sinai_holidays_with_names(year: int) -> List[Dict]:
        """
        Get Mount Sinai official holidays with names for calendar display
        Returns a list of dictionaries with date and name
        """
        holidays = []

        # New Year's Day - January 1
        new_years = date(year, 1, 1)
        observed = BusinessDaysCalculator.get_observed_date(new_years)
        holidays.append({
            'date': observed,
            'name': "New Year's Day",
            'observed': observed != new_years
        })

        # Martin Luther King Jr. Day - Third Monday in January
        jan_first = date(year, 1, 1)
        days_to_first_monday = (7 - jan_first.weekday()) % 7
        if jan_first.weekday() == 0:
            days_to_first_monday = 0
        first_monday = jan_first + timedelta(days=days_to_first_monday)
        mlk_day = first_monday + timedelta(days=14)
        holidays.append({
            'date': mlk_day,
            'name': 'Martin Luther King Jr. Day',
            'observed': False
        })

        # Presidents' Day - Third Monday in February
        feb_first = date(year, 2, 1)
        days_to_first_monday = (7 - feb_first.weekday()) % 7
        if feb_first.weekday() == 0:
            days_to_first_monday = 0
        first_monday = feb_first + timedelta(days=days_to_first_monday)
        presidents_day = first_monday + timedelta(days=14)
        holidays.append({
            'date': presidents_day,
            'name': "Presidents' Day",
            'observed': False
        })

        # Memorial Day - Last Monday in May
        may_31 = date(year, 5, 31)
        days_back_to_monday = (may_31.weekday() - 0) % 7
        memorial_day = may_31 - timedelta(days=days_back_to_monday)
        holidays.append({
            'date': memorial_day,
            'name': 'Memorial Day',
            'observed': False
        })

        # Juneteenth - June 19
        juneteenth = date(year, 6, 19)
        observed = BusinessDaysCalculator.get_observed_date(juneteenth)
        holidays.append({
            'date': observed,
            'name': 'Juneteenth',
            'observed': observed != juneteenth
        })

        # Independence Day - July 4
        independence_day = date(year, 7, 4)
        observed = BusinessDaysCalculator.get_observed_date(independence_day)
        holidays.append({
            'date': observed,
            'name': 'Independence Day',
            'observed': observed != independence_day
        })

        # Labor Day - First Monday in September
        sep_first = date(year, 9, 1)
        days_to_first_monday = (7 - sep_first.weekday()) % 7
        if sep_first.weekday() == 0:
            days_to_first_monday = 0
        labor_day = sep_first + timedelta(days=days_to_first_monday)
        holidays.append({
            'date': labor_day,
            'name': 'Labor Day',
            'observed': False
        })

        # Thanksgiving - Fourth Thursday in November
        nov_first = date(year, 11, 1)
        days_to_first_thursday = (3 - nov_first.weekday()) % 7
        if nov_first.weekday() == 3:
            days_to_first_thursday = 0
        first_thursday = nov_first + timedelta(days=days_to_first_thursday)
        thanksgiving = first_thursday + timedelta(days=21)
        holidays.append({
            'date': thanksgiving,
            'name': 'Thanksgiving',
            'observed': False
        })

        # Christmas Day - December 25
        christmas = date(year, 12, 25)
        observed = BusinessDaysCalculator.get_observed_date(christmas)
        holidays.append({
            'date': observed,
            'name': 'Christmas Day',
            'observed': observed != christmas
        })

        return holidays

    # Keep old method name for backwards compatibility
    @staticmethod
    def get_federal_holidays(year: int) -> Set[date]:
        """Alias for get_mount_sinai_holidays for backwards compatibility"""
        return BusinessDaysCalculator.get_mount_sinai_holidays(year)

    @staticmethod
    def is_business_day(check_date: date) -> bool:
        """
        Check if a given date is a business day
        Returns False for weekends and Mount Sinai holidays
        """
        # Check if it's a weekend (Saturday=5, Sunday=6)
        if check_date.weekday() >= 5:
            return False

        # Check if it's a Mount Sinai holiday
        year_holidays = BusinessDaysCalculator.get_mount_sinai_holidays(check_date.year)
        if check_date in year_holidays:
            return False

        return True

    @staticmethod
    def calculate_business_days(start_date: date, end_date: date) -> int:
        """
        Calculate the number of business days between two dates (inclusive)
        Excludes weekends and Mount Sinai holidays
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
        Excludes weekends and Mount Sinai holidays
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
            all_holidays.update(BusinessDaysCalculator.get_mount_sinai_holidays(year))

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


def get_holidays_for_calendar(year: int = None) -> List[Dict]:
    """
    Get holidays formatted for FullCalendar display
    Returns current year and next year if year not specified
    """
    if year is None:
        year = datetime.now().year

    holidays = []

    # Get holidays for current year and next year
    for y in [year, year + 1]:
        year_holidays = BusinessDaysCalculator.get_mount_sinai_holidays_with_names(y)
        for h in year_holidays:
            title = h['name']
            if h['observed']:
                title += ' (Observed)'
            holidays.append({
                'id': f"holiday_{h['date'].isoformat()}",
                'title': title,
                'start': h['date'].isoformat(),
                'end': h['date'].isoformat(),
                'color': '#6f42c1',  # Purple for holidays
                'allDay': True,
                'display': 'background',  # Show as background event
                'extendedProps': {
                    'type': 'holiday',
                    'is_holiday': True,
                    'observed': h['observed']
                }
            })

    return holidays


if __name__ == "__main__":
    # Test the calculator
    print("Mount Sinai Business Days Calculator Test")
    print("=" * 50)

    # Show 2025 holidays
    print("\nMount Sinai Holidays 2025:")
    holidays_2025 = BusinessDaysCalculator.get_mount_sinai_holidays_with_names(2025)
    for h in holidays_2025:
        observed = " (Observed)" if h['observed'] else ""
        print(f"  {h['name']}: {h['date'].strftime('%B %d, %Y')}{observed}")

    # Show 2026 holidays
    print("\nMount Sinai Holidays 2026:")
    holidays_2026 = BusinessDaysCalculator.get_mount_sinai_holidays_with_names(2026)
    for h in holidays_2026:
        observed = " (Observed)" if h['observed'] else ""
        print(f"  {h['name']}: {h['date'].strftime('%B %d, %Y')}{observed}")

    # Test case: Thursday to Tuesday (should exclude weekend)
    start = date(2025, 12, 18)  # Thursday
    end = date(2025, 12, 23)    # Tuesday

    info = BusinessDaysCalculator.get_holiday_info(start, end)
    print(f"\nDec 18-23, 2025 (Thu-Tue):")
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
