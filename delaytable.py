import pandas as pd
import numpy as np
import datetime as dt

class DelayTables:
    """Delay Tables Doc String """
    
    def __init__(self, start_year, end_year, month):
        self.month = month
        self.start_year = start_year
        self.end_year = end_year
    
    def delay_tables(self, directory='data'):
        flights = self.flight_tables()
        
        flights['arr_delay'] = flights.apply(
            lambda row: 0 if ( np.isnan(row['arr_delay']) & (row['cancelled'] == 0) ) else row['arr_delay'], axis=1
        )
        flights['arr_delay'] = flights.apply(
            lambda row: 0 if ( np.isnan(row['arr_delay']) & (row['diverted'] == 0) ) else row['arr_delay'], axis=1
        )
        
        def split_into_hours(series): 
            hours = np.empty(series.shape[0])
            for i, line in enumerate(series):
                line = str(line)
                if (len(line) == 2) or (len(line) == 1):
                    hours[i] = 0
                elif len(line) == 3:
                    hours[i] = line[0]
                elif len(line) == 4:
                    hours[i] = line[:2]
                else:
                    hours[i] = np.nan
            
            return hours
        
        
        def split_into_day(series): 
            days = np.empty(series.shape[0])
            for i, line in enumerate(series):
                line = str(line)
                if line[-2] == 0:
                    days[i] = int(line[-1])
                else:
                    days[i] = int(line[-2:])
            
            return days
        
        flights['dep_hr'] = split_into_hours(flights.crs_dep_time)
        flights['day'] = split_into_day(flights.fl_date)

        
        def average_dictionary(df):
            stat_dict = {}
            for index, row in df.iterrows():
                stat_dict[index] = row[0]

            return stat_dict

        summary = pd.DataFrame(flights[['arr_delay','dep_hr']].groupby('dep_hr').mean())
        hour_delay = average_dictionary(summary)

        summary = pd.DataFrame(flights[['arr_delay','day']].groupby('day').mean())
        daily_delay = average_dictionary(summary)
        
        summary = pd.DataFrame(flights[['arr_delay','mkt_carrier']].groupby('mkt_carrier').mean())
        carrier_delay = average_dictionary(summary)
        
        summary = pd.DataFrame(flights[['arr_delay','origin_city_name']].groupby('origin_city_name').mean())
        origin_city_delay = average_dictionary(summary)
        
        summary = pd.DataFrame(flights[['arr_delay','dest_city_name']].groupby('dest_city_name').mean())
        dest_city_delay = average_dictionary(summary)
 
        summary = pd.DataFrame(flights[['arr_delay','tail_num']].groupby('tail_num').mean())
        tail_delay = average_dictionary(summary)

        
        return hour_delay, daily_delay, carrier_delay, origin_city_delay, dest_city_delay, tail_delay#, taxi_out_delay, taxi_in_delay
     
    
    def flight_tables(self, directory='data'):
        paths = self.path_strings()
        if len(paths) == 1:
            flights = pd.read_csv(paths[0], low_memory=False)
        else:
            flight1 = pd.read_csv(paths[0], low_memory=False)
            flight2 = pd.read_csv(paths[1], low_memory=False)
            flights = pd.concat([flight1, flight2], axis=0)
            # flights = pd.concat(map(pd.read_csv, paths), ignore_index=True)
        
        return flights  
    
    
    def __month_path_string(self):
        m = str(self.month)
        if len(m) == 2:
            return m
        else:
            return '0' + m
    
    
    def __year_path_strings(self):
        year_path = []
        if self._start_year == self._end_year:
            year_path.append(str(self._start_year))
        else:
            year_path.extend((str(self._start_year), str(self._end_year)))
        
        return year_path
    
    def path_strings(self, directory='data'):
        year_strings = self.__year_path_strings()
        month_string = self.__month_path_string()
        paths = []
        for year in year_strings:
            path = directory + '/' + year + '-' + month_string + '.csv'
            paths.append(path)
        
        return paths
    
    
    @property
    def start_year(self):
        return self._start_year
    
    @start_year.setter
    def start_year(self, value):
        if value not in [2018, 2019]:
            raise ValueError("Start year and End year must be 2018 or 2019")
        self._start_year = value  
    
    @property
    def end_year(self):
        return self._end_year
    
    @start_year.setter
    def end_year(self, value):
        if value < self._start_year:
            raise ValueError("End year must be greater or equal to Start year")
        if value not in [2018, 2019]:
            raise ValueError("Start year and End year must be 2018 or 2019")
        self._end_year = value
    
    @property
    def month(self):
        return self._month
    
    @month.setter
    def month(self, value):
        if not isinstance(value, int):
            raise ValueError("Month must be an integer between 1 and 12")
        if not 0 < value < 13:
            raise ValueError("Month must be an integer between 1 and 12")
        self._month = value