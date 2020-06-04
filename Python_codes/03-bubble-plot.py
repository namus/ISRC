#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 21:03:40 2020

@author: Suman
"""

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls
from scipy import stats

username = 'sumanc' # your username
api_key = 'KMxiSODVgl4VlMLtpjMp' # your api key - go to profile > settings > regenerate key
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)

state_wise = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise.csv")
data = state_wise[state_wise['State_code'] != 'UN'][1:13]

data = data[['State','State_code','Confirmed','Recovered','Deaths','Active']]
data = data.loc[data['Confirmed'] > 10]
ratio = data['Deaths']/data['Recovered']
#ratio = data['Deaths']/(data['Recovered']+data['Deaths'])
data['D/R']=ratio
data['Positivity'] = 0.0
data['Rate'] = 0.0

testdata = pd.read_csv("https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv")
for mystate in data['State'].values:
    tested=testdata.loc[testdata['State']==mystate][['Updated On','Total Tested','Positive']].dropna()
    tested['Updated On']=tested['Updated On'].str.replace('2050', '2020')
    if mystate=='Kerala':
        tested['Updated On']=tested['Updated On'].str.replace('04/02/2020', '04/04/2020')
    tested['Updated On']=pd.to_datetime(tested['Updated On'],format='%d/%m/%Y')
    tested = tested.loc[tested['Total Tested'] > 0]
    tested['Positivity']=tested['Positive']/tested['Total Tested']
    data['Positivity'].loc[data['State']==mystate] = tested['Positivity'].values[-1]

startdate = pd.to_datetime('2019-12-31')
state_wise_daily = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")

today = state_wise_daily['Date'].tail(1)
today = pd.to_datetime(today.values[0])
todaystr = today.strftime('%d/%m/%Y')

for state in data['State'].values:
    mystate = data.loc[data['State']==state]['State_code'].values[0]
    new = state_wise_daily.loc[(state_wise_daily['Status'] == 'Confirmed')][['Date',mystate]].copy().dropna()
    new[mystate] = np.cumsum(new[mystate])
    new[mystate] = new[mystate].loc[new[mystate] > 10]
    new = new.dropna()
    log2=np.log2(new[mystate])
    
    date=pd.to_datetime(new['Date'])
    julian = (date - startdate).dt.days.values
 
    slope, intercept, r_value, p_value, std_err = stats.linregress(julian[-5:],log2.values[-5:])
    #print(mystate, slope)
    data['Rate'].loc[data['State']==state] = slope

fig = px.scatter(
    data,
    x='Positivity',
    y='D/R',
    size='Active',
    color='Rate',
    hover_name="State",
    text='State_code',
    log_x=False,
    size_max=100,
    #colorbar=dict(
    #    tickfont=dict(size=16),title=dict(size=16)),
    #height=600,
    #width=800,
    color_continuous_scale=px.colors.sequential.Plasma)

fig.update_xaxes(tickfont=dict(size=16),titlefont=dict(size=16),automargin=True)
fig.update_yaxes(tickfont=dict(size=16),titlefont=dict(size=16),automargin=True)

fig.update_layout(title_text='<b>State-wise parameters (as on '+todaystr+')</b><br>Size: Active Cases; Color: Growth Rate Constant<br><i>Data Source: api.covid19india.org</i>', title_x=0.5)
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
        font=dict(
            size=16,
        ),
    )
)
fig.update_layout(
    margin=dict(l=40, r=40, t=100, b=40),
    )

fig.write_image("COVID19-phase-plot.pdf", scale=2)
#py.plot(fig, filename = 'COVID19-phase-plot', auto_open=False)

