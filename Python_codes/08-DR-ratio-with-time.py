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

state_wise = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise.csv")
state_wise = state_wise[state_wise['State_code'] != 'UN']
state_wise_daily = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")

top12 = list(state_wise[:12]['State_code'])
top12_full = list(state_wise[:12]['State'])
top12_full[0]='India'

startdate = pd.to_datetime('2019-12-31')
lockdown=pd.to_datetime('2020-03-25')
today = state_wise_daily['Date'].tail(1)
today = pd.to_datetime(today.values[0])
todaystr = today.strftime('%d/%m/%Y')

# Doubling time for top states ...
fig = make_subplots(
    rows=4, cols=3,
    subplot_titles=top12_full,
#    shared_yaxes=True
    )

idx = 0
for row in range(1,5):
    for col in range(1,4):
        mystate = top12[idx]
        #print(mystate)
        conf = state_wise_daily.loc[(state_wise_daily['Status'] == 'Confirmed')][['Date',mystate]].copy().dropna()
        rec = state_wise_daily.loc[(state_wise_daily['Status'] == 'Recovered')][['Date',mystate]].copy().dropna()
        dec = state_wise_daily.loc[(state_wise_daily['Status'] == 'Deceased')][['Date',mystate]].copy().dropna()
        
        conf[mystate] = np.cumsum(conf[mystate])
        rec[mystate] = np.cumsum(rec[mystate])
        dec[mystate] = np.cumsum(dec[mystate])
        
        merged = pd.merge(conf, rec, on="Date")
        merged = pd.merge(merged, dec, on="Date")
        merged = merged.rename(columns={merged.keys()[1]: "Confirmed", merged.keys()[2]: "Recovered", merged.keys()[3]: "Deceased"})
        
        merged['Active'] = merged['Confirmed'] - (merged['Deceased']+merged['Recovered'])
        
        merged = merged.loc[merged['Recovered'] > 10]
        merged['D/R'] = merged['Deceased']/merged['Recovered']

        #merged['D/R'] = merged['Deceased']/(merged['Deceased'] + merged['Recovered'])
        #merged = merged.loc[merged['D/R'] < 1]

        date=pd.to_datetime(merged['Date'])
        julian = (date - startdate).dt.days.values
        lockdown=pd.to_datetime('2020-03-25')
        
        y = merged['D/R']

        fig.add_trace(go.Scatter(
        x=date,
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
        y=[0,y.max()],
        mode='lines',
        line=dict(color="#000000",dash="dash",width=2),
        ),
        row=row, col=col,)
        '''

        idx += 1

fig.update_yaxes(range=[0, 0.4])
fig.update_layout(height=1000, width=1000,
                 title_text='<b>Death/Recovered Ratio (as on '+todaystr+')</b><br><i>Data Source: api.covid19india.org</i>', title_x=0.5,showlegend=False,template='ggplot2')

fig.update_layout(images=[dict(
        source="https://raw.githubusercontent.com/namus/ISRC/master/Images/ISRC_Logo_JPEG.jpg",
        xref="paper", yref="paper",
        x=1.2, y=1.0,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
      )],
        )

fig.write_image("COVID19-DR-ratio.pdf",height=1000, width=1000,scale=2)
#py.plot(fig, filename = 'COVID19-DR-ratio', auto_open=False)

