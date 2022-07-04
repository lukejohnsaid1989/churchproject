import requests as re
import json
from datetime import date, timedelta
import pandas as pd
import streamlit as st
import os

class LiturgicalCalendar:
    def __init__(self, today=date.today()):
        self.today = today

    @staticmethod
    def get_week(weekday):
        weekstart = weekday - timedelta(days=weekday.weekday())
        weekend = weekstart + timedelta(days=6)

        def get_date_range(start, end):
            ls = []
            x = 0
            while True:
                temp = start + timedelta(days=x)
                if temp <= end:
                    ls.append(temp)
                else:
                    break
                x += 1
            return ls

        return get_date_range(weekstart, weekend)

    @staticmethod
    def get_api_date(api_date):
        resp = re.get(
            f"http://calapi.inadiutorium.cz/api/v0/en/calendars/default/{api_date.year}/{api_date.month}/{api_date.day}")
        d = json.loads(resp.content)
        return d

    @staticmethod
    def parse_dates_df(ls):
        df = pd.DataFrame(ls)
        ls = []
        for row in df.iterrows():
            for feast in row[1].celebrations:
                d = {"date": row[1].date}
                for key, value in feast.items():
                    d[key] = value
                ls.append(d)
        dff = pd.DataFrame(ls).merge(df, on="date").drop(columns="celebrations")
        return dff.query("rank != 'ferial'")

    def get_liturgical_calendar_this_week(self):
        return [self.get_api_date(i) for i in self.get_week(weekday=self.today)]

    def parse_liturgical_calendar_this_week(self):
        return self.parse_dates_df(self.get_liturgical_calendar_this_week())

    def get_liturgical_calendar_next_week(self):
        return [self.get_api_date(i) for i in self.get_week(weekday=self.today + timedelta(days=7))]

    def parse_liturgical_calendar_next_week(self):
        return self.parse_dates_df(self.get_liturgical_calendar_next_week())

if __name__ == '__main__':
    st.header("Liturgical Calendar")
    st.write("Api: http://calapi.inadiutorium.cz/")
    calendar_holder = st.date_input(label="choose date",value=date.today())
    jesus = LiturgicalCalendar(today=calendar_holder)
    st.header("Feasts this week")
    df = jesus.parse_liturgical_calendar_this_week()
    st.write(df)
    st.header("Feasts next week")
    dff = jesus.parse_liturgical_calendar_next_week()
    st.write(dff)
    st.download_button(data=pd.concat([df,dff]).to_csv(index=False),label="download",file_name=f"liturgical_calendar_{str(calendar_holder).replace('-','')}.csv")
