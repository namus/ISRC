#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:38:53 2020

@author: Suman
"""
import pandas as pd
import numpy as np
from scipy import signal
from scipy import stats

import datetime

import plotly.express as px
import plotly.graph_objects as go

import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls

username = 'sumanc' # your username
api_key = 'KMxiSODVgl4VlMLtpjMp' # your api key - go to profile > settings > regenerate key
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)

def add_bar(data):
    conf_tot = state_wise.iloc[0][data]
    x = state_wise['State'][1:]
    y = 100*(state_wise[data][1:]/conf_tot)
    
    fig.add_trace(go.Bar(
        x=x[:num],
        y=y[:num],
        name=data,
        #marker_color='indianred'
    ))    

num = 12
state_wise = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise.csv")
state_wise = state_wise[state_wise['State_code'] != 'UN']
state_wise_daily = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")
testdata = pd.read_csv("https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv")

today = state_wise_daily['Date'].tail(1)
today = pd.to_datetime(today.values[0])
todaystr = today.strftime('%d/%m/%Y')

startdate = pd.to_datetime('2019-12-31')

top12 = list(state_wise[:num+1]['State_code'])
top12_full = list(state_wise[:num+1]['State'])
top12_full[0]='India'
allstates = testdata['State'].unique()

India = 0
India_pos = 0

for mystate in allstates:
    tested=testdata.loc[testdata['State']==mystate][['Updated On','Total Tested','Positive']].dropna()
    tested['Updated On']=tested['Updated On'].str.replace('2050', '2020')
    if mystate=='Kerala':
        tested['Updated On']=tested['Updated On'].str.replace('04/02/2020', '04/04/2020')
    tested['Updated On']=pd.to_datetime(tested['Updated On'],format='%d/%m/%Y')
    tested = tested.loc[tested['Total Tested'] >= 1]
    tested['Positivity']=tested['Positive']/tested['Total Tested']

    India += tested['Total Tested'].values[-1]
    India_pos += tested['Positive'].values[-1]

state_wise['Total Tested'] = 0.0
state_wise['Positivity'] = 0.0

for mystate in top12_full[1:]:
    tested=testdata.loc[testdata['State']==mystate][['Updated On','Total Tested','Positive']].dropna()
    tested['Updated On']=tested['Updated On'].str.replace('2050', '2020')
    if mystate=='Kerala':
        tested['Updated On']=tested['Updated On'].str.replace('04/02/2020', '04/04/2020')
    tested['Updated On']=pd.to_datetime(tested['Updated On'],format='%d/%m/%Y')
    tested = tested.loc[tested['Total Tested'] >= 1]
    tested['Positivity']=tested['Positive']/tested['Total Tested']
    state_wise['Total Tested'].loc[state_wise['State']==mystate] = tested['Total Tested'].values[-1]
    state_wise['Positivity'].loc[state_wise['State']==mystate] = (tested['Positive'].values[-1])/(tested['Total Tested'].values[-1])

state_wise['Total Tested'] = 100*(state_wise['Total Tested']/India)
state_wise['Positivity'].loc[state_wise['State']=='Total'] = India_pos/India

fig = go.Figure()

# Add bar chart for Confirmed cases ...
add_bar('Confirmed')

# Add bar chart for Deaths ...
add_bar('Deaths')

# Add bar chart for Recovered cases ...
add_bar('Recovered')

# Add bar chart for Active cases ...
add_bar('Active')

# Add bar chart for Tested ...

fig.add_trace(go.Bar(
    x= state_wise['State'][1:num+1],
    y= state_wise['Total Tested'][1:num+1],
    name='Samples Tested',
    #marker_color='indianred'
))    

fig.update_yaxes(tickfont=dict(size=16),titlefont=dict(size=18))
fig.update_xaxes(tickfont=dict(family='Rockwell', color='crimson', size=16), showgrid=False)
fig.update_layout(barmode='group', xaxis_tickangle=-45)
fig.update_layout(title_text='<b>State-wise contribution (as on '+todaystr+')</b><br><i>Data Source: api.covid19india.org</i>', title_x=0.5,
                 yaxis_title='Percentage')
fig.update_layout(images=[dict(
        source="https://raw.githubusercontent.com/namus/ISRC/master/Images/ISRC_Logo_JPEG.jpg",
        xref="paper", yref="paper",
        x=1.1, y=1.0,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
      )],
        )
fig.update_layout(
    legend=dict(
        x=0.6, y=0.9,
        font=dict(
            size=16,
        ),
    )
)

#fig.show()
fig.write_image("COVID19-Histogram-Simple-Data.pdf",scale=2)
##py.plot(fig, filename = 'COVID19-Histogram-Simple-Data', auto_open=False)

