from datetime import datetime, timedelta, date


def all_saturdays(year):
    """
    Gets all the Saturdays in a given year
    """
    saturdays = []
    d = date(year, 1, 1)
    d += timedelta(days=5 - d.weekday())
    while d.year == year:
        saturdays.append(d.strftime('%Y-%m-%d'))
        d += timedelta(days=7)
    return saturdays


def next_weekday(d, weekday):
    """
    Gets the date of the weekday that is after
    the given day
    """
    date_obj = datetime.strptime(d, '%Y-%m-%d')
    days_ahead = weekday - date_obj.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return (date_obj + timedelta(days_ahead)).strftime('%Y-%m-%d')


def get_all_weeks():
    """
    Return a list of all the Saturdays from October 4th, 2014
    """
    start_date = '2014-10-04'
    start_year = 2014
    today = datetime.today().strftime('%Y-%m-%d')
    end_date = next_weekday(today, 5)
    end_year = datetime.strptime(end_date, '%Y-%m-%d').year
    year_counter = start_year
    all_weeks = []
    while year_counter <= end_year:
        yearly_saturdays = all_saturdays(year_counter)
        if year_counter == start_year:
            yearly_saturdays = [
                d for d in yearly_saturdays if (d >= start_date)]
        if year_counter == end_year:
            yearly_saturdays = [d for d in yearly_saturdays if (d <= end_date)]
        all_weeks.extend(yearly_saturdays)
        year_counter += 1
    return all_weeks
