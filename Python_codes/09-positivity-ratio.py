#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 21:02:59 2020

@author: Suman
"""

import pandas as pd
import numpy as np
from scipy import signal
from scipy import stats

import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls

username = 'sumanc' # your username
api_key = 'KMxiSODVgl4VlMLtpjMp' # your api key - go to profile > settings > regenerate key
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)

todaystr = datetime.datetime.now().strftime('%d/%m/%Y')

testdata = pd.read_csv("https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv")
state_wise = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise.csv")
state_wise = state_wise[state_wise['State_code'] != 'UN']
state_wise_daily = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")

top12 = list(state_wise[:13]['State_code'])
top12_full = list(state_wise[:13]['State'])
top12_full[0]='India'
states = testdata['State'].unique()

'''
for mystate in top12_full[1:18]:
    tested=testdata.loc[testdata['State']==mystate][['Updated On','Total Tested','Positive']].dropna()
    tested['Updated On']=tested['Updated On'].str.replace('2050', '2020')
    tested['Updated On']=pd.to_datetime(tested['Updated On'],format='%d/%m/%Y')
    tested['Positivity']=tested['Positive']/tested['Total Tested'] 
'''

startdate = pd.to_datetime('2019-12-31')
lockdown=pd.to_datetime('2020-03-25')
today = state_wise_daily['Date'].tail(1)
today = pd.to_datetime(today.values[0])
todaystr = today.strftime('%d/%m/%Y')

# Doubling time for top states ...
fig = make_subplots(
    rows=4, cols=3,
    subplot_titles=top12_full[1:13],
#    shared_yaxes=True
    )

idx = 0
for row in range(1,5):
    for col in range(1,4):
        mystate = top12_full[1:13][idx]
        
        tested=testdata.loc[testdata['State']==mystate][['Updated On','Total Tested','Positive']].dropna()
        tested['Updated On']=tested['Updated On'].str.replace('2050', '2020')
        if mystate=='Kerala':
            tested['Updated On']=tested['Updated On'].str.replace('04/02/2020', '04/04/2020')
        tested['Updated On']=pd.to_datetime(tested['Updated On'],format='%d/%m/%Y')
        tested = tested.loc[tested['Total Tested'] >= 1]
        tested['Positivity']=tested['Positive']/tested['Total Tested']
        
        date=pd.to_datetime(tested['Updated On'])
        julian = (date - startdate).dt.days.values

        x = date
        #y = tested['Total Tested'] # tested['Positivity']
        y = tested['Positivity']

        fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        marker=dict(
            size=4,
            )
        ),
        row=row, col=col)

        '''
        fig.add_trace(go.Scatter(
        x=[lockdown,lockdown],
        y=[y.min(),y.max()],
        mode='lines',
        line=dict(color="#000000",dash="dash",width=2),
        ),
        row=row, col=col,)
        '''

        idx += 1

fig.update_yaxes(range=[0, 0.12])
fig.update_layout(height=1000, width=1000,
#                 title_text='Number of tests performed (as on '+todaystr+')</b><br><i>Data Source: api.covid19india.org</i>', title_x=0.5,showlegend=False,template='ggplot2')
                 title_text='<b>Test Positivity (as on '+todaystr+')</b><br><i>Data Source: api.covid19india.org</i>', title_x=0.5,showlegend=False,template='ggplot2')

fig.update_layout(images=[dict(
        source="https://raw.githubusercontent.com/namus/ISRC/master/Images/ISRC_Logo_JPEG.jpg",
        xref="paper", yref="paper",
        x=1.2, y=1.0,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
      )],
        )

#fig.write_image("COVID19-test-positivity.pdf",height=1000, width=1000,scale=2)
py.plot(fig, filename = 'COVID19-test-positivity', auto_open=False)

