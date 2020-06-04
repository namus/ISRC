#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 21:02:59 2020

@author: Suman
"""

import pandas as pd
import numpy as np
from scipy import signal
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

top12 = list(state_wise[:12]['State_code'])
top12_full = list(state_wise[:12]['State'])
top12_full[0]='India'
states = testdata['State'].unique()

startdate = pd.to_datetime('2019-12-31')
lockdown=pd.to_datetime('2020-03-25')
today = state_wise_daily['Date'].tail(1)
today = pd.to_datetime(today.values[0])
todaystr = today.strftime('%d/%m/%Y')

# Doubling time for top states ...
fig = make_subplots(
    rows=4, cols=3,
    subplot_titles=top12_full
    )

idx = 0
for row in range(1,5):
    for col in range(1,4):
        mystate = top12[idx]
        #print(mystate)
        conf = state_wise_daily.loc[(state_wise_daily['Status'] == 'Confirmed')][['Date',mystate]].copy().dropna()
        rec = state_wise_daily.loc[(state_wise_daily['Status'] == 'Recovered')][['Date',mystate]].copy().dropna()
        dec = state_wise_daily.loc[(state_wise_daily['Status'] == 'Deceased')][['Date',mystate]].copy().dropna()
        #if np.any(conf[mystate].values < 0):
        #    print("DEBUG: ",mystate,conf[mystate].values)
        conf[mystate] = np.cumsum(np.abs(conf[mystate]))
        rec[mystate] = np.cumsum(np.abs(rec[mystate]))
        dec[mystate] = np.cumsum(np.abs(dec[mystate]))
        
        merged = pd.merge(conf, rec, on="Date")
        merged = pd.merge(merged, dec, on="Date")
        merged = merged.rename(columns={merged.keys()[1]: "Confirmed", merged.keys()[2]: "Recovered", merged.keys()[3]: "Deceased"})
        
        merged['Active'] = merged['Confirmed'] - (merged['Deceased']+merged['Recovered'])

        mystate = top12_full[idx]
        tested=testdata.loc[testdata['State']==mystate][['Updated On','Total Tested','Positive']].dropna()
        tested['Updated On']=tested['Updated On'].str.replace('2050', '2020')
        if mystate=='Kerala':
            tested['Updated On']=tested['Updated On'].str.replace('04/02/2020', '04/04/2020')
        tested['Updated On']=pd.to_datetime(tested['Updated On'],format='%d/%m/%Y')
        tested = tested.loc[tested['Total Tested'] >= 1]
        tested['Positivity']=tested['Positive']/tested['Total Tested']
        
        #merged = merged.loc[merged['Recovered'] > 0]
        #merged['D/R'] = merged['Deceased']/(merged['Deceased'] + merged['Recovered'])
        #merged = merged.loc[merged['D/R'] < 1]

        merged['Date']=pd.to_datetime(merged['Date'])
        lockdown=pd.to_datetime('2020-03-25')
        merged = merged[merged['Date'] >= lockdown]
        date = merged['Date']
        julian = (date - startdate).dt.days.values
        
        y1 = merged['Confirmed']
        y2 = merged['Active']
        y3 = merged['Recovered']
        y4 = merged['Deceased']*10
        y5 = tested['Total Tested']/10
        
        if idx==(len(top12)-1):
            fig.add_trace(go.Scatter(
            x=date,
            y=y1,
            name='Confirmed',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
            showlegend=True,
            ),
            row=row, col=col)
    
            fig.add_trace(go.Scatter(
            x=date,
            y=y2,
            name='Active',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=True,
            ),
            row=row, col=col)
    
            fig.add_trace(go.Scatter(
            x=date,
            y=y3,
            name='Recovered',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=True,
            ),
            row=row, col=col)
    
            fig.add_trace(go.Scatter(
            x=date,
            y=y4,
            name='Deceased (X 10)',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=True,
    
            ),
            row=row, col=col)

            '''
            fig.add_trace(go.Scatter(
            x=date,
            y=y5,
            name='Samples tested (/ 10)',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=True,
    
            ),
            row=row, col=col)
            '''  

            fig.add_trace(go.Scatter(
            x=[lockdown,lockdown],
            y=[0,merged['Confirmed'].max()],
            mode='lines',
            name='Lockdown',
            line=dict(color="#000000",dash="dash",width=2),
                    showlegend=True,
            ),
            row=row, col=col,)
        else:
            fig.add_trace(go.Scatter(
            x=date,
            y=y1,
            name='Confirmed',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
            showlegend=False,
            ),
            row=row, col=col)
    
            fig.add_trace(go.Scatter(
            x=date,
            y=y2,
            name='Active',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=False,
            ),
            row=row, col=col)
    
            fig.add_trace(go.Scatter(
            x=date,
            y=y3,
            name='Recovered',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=False,
            ),
            row=row, col=col)
    
            fig.add_trace(go.Scatter(
            x=date,
            y=y4,
            name='Deceased (X 10)',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=False,
    
            ),
            row=row, col=col)

            '''
            fig.add_trace(go.Scatter(
            x=date,
            y=y5,
            name='Samples tested (/ 10)',
            mode='lines+markers',
            marker=dict(
                size=4,
                ),
                    showlegend=False,
    
            ),
            row=row, col=col)
            '''
 
            fig.add_trace(go.Scatter(
            x=[lockdown,lockdown],
            y=[0,merged['Confirmed'].max()],
            mode='lines',
            name='Lockdown',
            line=dict(color="#000000",dash="dash",width=2),
                    showlegend=False,
            ),
            row=row, col=col,)

        idx += 1

fig.update_layout(height=1000, width=1000,
                 title_text='<b>National and state-wise numbers of reported cases (as on '+todaystr+')</b><br><i>Data Source: api.covid19india.org</i>', title_x=0.5,showlegend=True,template='ggplot2',
                 )

fig.update_layout(images=[dict(
        source="https://raw.githubusercontent.com/namus/ISRC/master/Images/ISRC_Logo_JPEG.jpg",
        xref="paper", yref="paper",
        x=1.2, y=1.0,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
      )],
        )

fig.write_image("COVID19-state-wise-time-evolution.pdf",height=1000, width=1000,scale=2)
#py.plot(fig, filename = 'COVID19-state-wise-time-evolution', auto_open=False)
