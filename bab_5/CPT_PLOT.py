import xlwings as xw
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#membaca file dan nama_sheet excel
sheet1 = xw.Book(r'CPT SBT.xlsm').sheets['start']
#general properties dataframe
df_general= sheet1['B3:D8'].options(pd.DataFrame,index=True).value.reset_index().dropna(subset=['properties']) #cara 1
df_general
#cpt dataframe
df_cpt= sheet1.range('B10').expand().options(pd.DataFrame,index=False).value    #cara 2
df_cpt

#analisis dengan metode SBY
#menentukan parameter awal
#Ic or I - SBT
type1 = 'clay - organic soil'
type2 = 'clays: clay to silty clay'
type3 = 'silt mixtures: clayey silt & silty clay'
type4 = 'sand mixtures: silty sand to sandy silt'
type5 = 'sand: clean sands to silty sands'
type6 = 'dense sand to gravelly sand'

#SBT zone
zone2 = 2   #'clay - organic soil'
zone3 = 3   #'clays: clay to silty clay'
zone4 = 4   #'silt mixtures: clayey silt & silty clay'
zone5 = 5   #'sand mixtures: silty sand to sandy silt'
zone6 = 6   #'sand: clean sands to silty sands'
zone7 = 7   #'dense sand to gravelly sand'
#SBT analysis. update dataframe df_cpt
#menentukan jenis tanah berdasarkan I-SBT pada tiap-tiap row dataframe CPT
def soil_type(x):
    qc = x['qc (MPa)']
    rf = x['Rf(%)']
    qc_pa = qc * 1000 / 101.325

    I_SBT = ((3.47 - np.log10(qc_pa)) ** 2 + (np.log10(rf) + 1.22) ** 2) ** 0.5

    if I_SBT > 3.6:
        return type1.title()
    elif (I_SBT > 2.95 and I_SBT <= 3.6):
        return type2.title()
    elif (I_SBT > 2.6 and I_SBT <= 2.95):
        return type3.title()
    elif (I_SBT > 2.05 and I_SBT <= 2.6):
        return type4.title()
    elif (I_SBT > 1.31 and I_SBT <= 2.05):
        return type5.title()
    elif (I_SBT <= 1.31):
        return type6.title()

df_cpt = df_cpt.assign(jenis_tanah=df_cpt.apply(soil_type, axis=1))
#SBT analysis. update dataframe df_cpt
#menghitung Ic SBT

def ic_sbt(x):
    qc = x['qc (MPa)']
    rf = x['Rf(%)']
    qc_pa = qc * 1000 / 101.325

    return ((3.47 - np.log10(qc_pa)) ** 2 + (np.log10(rf) + 1.22) ** 2) ** 0.5

df_cpt = df_cpt.assign(I_SBT=df_cpt.apply(ic_sbt, axis=1))

#SBT analysis. update dataframe df_cpt
#menentukan zona berdasarkan jenis tanah

def zone_calculation(x):
    if x['jenis_tanah'] == type1.title():
        return zone2
    elif x['jenis_tanah'] == type2.title():
        return zone3
    elif x['jenis_tanah'] == type3.title():
        return zone4
    elif x['jenis_tanah'] == type4.title():
        return zone5
    elif x['jenis_tanah'] == type5.title():
        return zone6
    elif x['jenis_tanah'] == type6.title():
        return zone7

df_cpt = df_cpt.assign(zone_SBT=df_cpt.apply(zone_calculation, axis=1))
df_cpt
#membuat target sheet baru
sheet2 = xw.Book(r'CPT SBT.xlsm').sheets['summary']

#mengisi sheet baru - summary dengan hasil analysis
sheet2['A1'].value = df_cpt
#plot cpt
fig = make_subplots(rows=1, cols=4, subplot_titles=("", "", ""), shared_yaxes=False,column_widths=[0.2, 0.2, 0.2, 0.4])

max_depth_cpt = max(df_cpt['Depth (m)'])

#FIGURE 1
fig.add_trace(go.Scatter(x=df_cpt['qc (MPa)'], y=df_cpt['Depth (m)'],name='qc', mode='lines', legendgroup = '2'), row=1, col=1)

#FIGURE 2
fig.add_trace(go.Scatter(x=df_cpt['Rf(%)'], y=df_cpt['Depth (m)'],name='fr', legendgroup = '2'), row=1, col=2)

#FIGURE 3
fig.add_trace(go.Scatter(x=df_cpt['I_SBT'], y=df_cpt['Depth (m)'],name='Ic', line_color='black', legendgroup = '2'), row=1, col=3)
fig.add_vrect(x0=0, x1=1.31, annotation_text="", annotation_position="top left", fillcolor="brown", opacity=0.45, line_width=0, row=1, col=3)
fig.add_vrect(x0=1.31, x1=2.05, annotation_text="", annotation_position="top left", fillcolor="orange", opacity=0.45, line_width=0, row=1, col=3)
fig.add_vrect(x0=2.05, x1=2.6, annotation_text="", annotation_position="top left", fillcolor="darkturquoise", opacity=0.45, line_width=0, row=1, col=3)
fig.add_vrect(x0=2.6, x1=2.95, annotation_text="", annotation_position="top left", fillcolor="green", opacity=0.45, line_width=0, row=1, col=3)
fig.add_vrect(x0=2.95, x1=3.6, annotation_text="", annotation_position="top left", fillcolor="pink", opacity=0.45, line_width=0, row=1, col=3)
fig.add_vrect(x0=3.6, x1=4.0, annotation_text="", annotation_position="top left", fillcolor="red", opacity=0.45, line_width=0, row=1, col=3)

#FIGURE 4
fig.add_trace(go.Bar(x=df_cpt.query('zone_SBT == 2')['zone_SBT'], y=df_cpt.query('zone_SBT == 3')['Depth (m)'], orientation='h', legendgroup = '3',name=f'{type1}',marker=dict( color='red',opacity=0.45, line=dict(color='red', width=1) )), row=1, col=4)

fig.append_trace(go.Bar(x=df_cpt.query('zone_SBT == 3')['zone_SBT'], y=df_cpt.query('zone_SBT == 3')['Depth (m)'], orientation='h', legendgroup = '3',name=f'{type2}',marker=dict( color='pink',opacity=0.45, line=dict(color='pink', width=1) )), row=1, col=4)

fig.append_trace(go.Bar(x=df_cpt.query('zone_SBT == 4')['zone_SBT'], y=df_cpt.query('zone_SBT == 4')['Depth (m)'], orientation='h', legendgroup = '3',name=f'{type3}',marker=dict( color='green',opacity=0.45, line=dict(color='green', width=1) )), row=1, col=4)

fig.append_trace(go.Bar(x=df_cpt.query('zone_SBT == 5')['zone_SBT'], y=df_cpt.query('zone_SBT == 5')['Depth (m)'], orientation='h', legendgroup = '3',name=f'{type4}',marker=dict( color='darkturquoise',opacity=0.45, line=dict(color='darkturquoise', width=1) )), row=1, col=4)

fig.append_trace(go.Bar(x=df_cpt.query('zone_SBT == 6')['zone_SBT'], y=df_cpt.query('zone_SBT == 6')['Depth (m)'], orientation='h', legendgroup = '3',name=f'{type5}',marker=dict( color='orange',opacity=0.45, line=dict(color='orange', width=1) )), row=1, col=4)

fig.append_trace(go.Bar(x=df_cpt.query('zone_SBT == 7')['zone_SBT'], y=df_cpt.query('zone_SBT == 7')['Depth (m)'], orientation='h', legendgroup = '3',name=f'{type6}',marker=dict( color='brown',opacity=0.45, line=dict(color='brown', width=1) )), row=1, col=4)

# Update xaxis properties
fig.update_xaxes(title_text="qc(MPa)", row=1, col=1, side ="top",range=[0,25], tickmode = 'linear', tick0 = 0, dtick = 5 , linecolor='black', gridcolor='LightPink', minor_griddash="dot",title_standoff = 0 )
fig.update_xaxes(title_text="rf(%)", row=1, col=2, side ="top",range=[0,6], tickmode = 'linear', tick0 = 0, dtick = 1, linecolor='black', gridcolor='LightPink',title_standoff = 0 )
fig.update_xaxes(title_text="SBT index", row=1, col=3, side ="top",range=[1,4], tickmode = 'linear', tick0 = 0, dtick = 0.5, linecolor='black',title_standoff = 0 )
fig.update_xaxes(title_text="Soil Behaviour Type", row=1, col=4, side ="top",range=[0,7], tickmode = 'linear', tick0 = 0, dtick = 1, linecolor='black',title_standoff = 0 )

# Update yaxis properties
fig.update_yaxes(title_text="Depth (m)", row=1, col=1, range=[max_depth_cpt,0], tickmode = 'linear', tick0 = 0, dtick = 1, linecolor='black', gridcolor='LightPink', minor_griddash="dot",title_standoff = 0 )
fig.update_yaxes(title_text="Depth (m)", row=1, col=2, range=[max_depth_cpt,0],tickmode = 'linear', tick0 = 0, dtick = 1, linecolor='black', gridcolor='LightPink',title_standoff = 0 )
fig.update_yaxes(title_text="Depth (m)", row=1, col=3, range=[max_depth_cpt,0],tickmode = 'linear', tick0 = 0, dtick = 1, linecolor='black',title_standoff = 0 )
fig.update_yaxes(title_text="Depth (m)", row=1, col=4, range=[max_depth_cpt,0],tickmode = 'linear', tick0 = 0, dtick = 1, linecolor='black',title_standoff = 0 )

# Update title and height
fig.update_layout(title_text="", width = 1300, height=800, legend_tracegroupgap=20, plot_bgcolor='rgb(245,245,240)', bargap=0,bargroupgap=0)

#tampilkan
sheet1.pictures.add(fig, name='plot sondir', update=True, left=sheet1.range('G11').left, top=sheet1.range('G11').top)