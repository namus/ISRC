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
        new = state_wise_daily.loc[(state_wise_daily['Status'] == 'Confirmed')][['Date',mystate]].copy().dropna()
        new[mystate] = np.cumsum(np.abs(new[mystate]))
        #new[mystate] = new[mystate].loc[new[mystate] >= 10]
        new = new.loc[new[mystate] >= 50]
        #new = new.dropna()
        #log2=new[mystate]
        log2=np.log2(new[mystate])
        
        date=pd.to_datetime(new['Date'])
        julian = (date - startdate).dt.days.values
        # New addition
        new['Date']=julian
        #new.to_csv(mystate+'.csv',index=False)

        #rate = np.gradient(signal.savgol_filter(log2,7,3),julian,edge_order=2)
        #td = 1.0/rate
        
        
        wsize = 5
        fitrange=julian.size - 2*(wsize//2)
        rate3 = np.zeros(fitrange)
        for i in range(fitrange):
            slope, intercept, r_value, p_value, std_err = stats.linregress(julian[i:i+wsize],log2.values[i:i+wsize])
            rate3[i] = slope
        

        fig.add_trace(go.Scatter(
        #x=date[2:-2],
        x=date[(wsize//2):-(wsize//2)],
        #y=td[2:-2],
        y=1.0/rate3,
        mode='lines+markers',
        marker=dict(
            size=4,
            )
        ),
        row=row, col=col)

        fig.add_trace(go.Scatter(
        x=[lockdown,lockdown],
        #y=[0,td[2:-2].max()], 
        y=[0,(1.0/rate3).max()],
        mode='lines',
        line=dict(color="#000000",dash="dash",width=2),
        ),
        row=row, col=col,)

        idx += 1

fig.update_yaxes(range=[0, 25])
fig.update_layout(height=1000, width=1000,
                 title_text='<b>Doubling time of confirmed cases (in days) (as on '+todaystr+')</b><br><i>Data Source: api.covid19india.org</i>', title_x=0.5,showlegend=False,template='ggplot2')

fig.update_layout(images=[dict(
        source="https://raw.githubusercontent.com/namus/ISRC/master/Images/ISRC_Logo_JPEG.jpg",
        xref="paper", yref="paper",
        x=1.2, y=1.0,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
      )],
        )
fig.update_layout(
    legend=dict(
        font=dict(
            size=16,
        ),
    )
)

#fig.show()
fig.write_image("COVID19-Doubling-time.pdf",height=1000, width=1000,scale=2)
#py.plot(fig, filename = 'COVID19-Doubling-time', auto_open=False)
