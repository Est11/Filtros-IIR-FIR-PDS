
#############################
# Creado por:			    #
# Esteban Restrepo Sierra   #
#############################


############################# LIBRERIAS UTILIZADAS #########################################
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np 
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import scipy.signal as sp
from scipy.io.wavfile import read 
from IPython.display import Audio 
from matplotlib.pylab import *
from scipy.io.wavfile import write
from playsound import playsound
import winsound as ws
############################################################################################

################# CARGANDO ENTORNO DE DASH , COLORES DE FONDO TEXTO Y GRAFICAS #############
app = dash.Dash()
app.config['suppress_callback_exceptions']=True
colors = {
    'background': '#7FDFF',
    'text': '#111111',
    'graf': '#332222'
}
###############################################################################################
nombre=' '
h=[] 
salida=''
####################### ENTORNO GRAFICO PRINCIPAL DE PAGINA WEB ###############################
# Aqui se encuentran primeras listas desplegables con  tipo de filtro IIR o FIR y comportamiento
# si es pasa-bajas, pasa-altas o pasa-banda y un boton que controla el flujo de los datos
app.layout = html.Div(style={'backgroundColor': colors['background']},children=[
    html.H1(
    	children='Parcial 3 PDS',
    	style={
            'textAlign': 'center',
            'color': colors['text']
    }),
    	
    html.H2(children='Esteban Restrepo Sierra  C.C xxxxxxxxx', style={
        'textAlign': 'center',
        'color': colors['text'],
    }),
    html.H2(
	   	children='DISEÑO DE UN FILTRO',
	   	style={
	        'textAlign': 'center',
		    'color': colors['text']
	}),
	html.Hr(),
    html.Div(style={'backgroundColor':colors['background']},children=[
	   	html.H3(html.Label('Tipo'),style={'textAlign':'center'}),
	    dcc.Dropdown(id='tipo_filtro',
	        options=[
	            {'label': 'Filtro FIR', 'value': 'FIR'},
	            {'label': u'Filtro IIR', 'value': 'IIR'},

	        ],
	        value=' '
	    ),  
	    html.Hr(),
	    html.H3(html.Label('Comportamiento'),style={'textAlign':'center'}),
	    dcc.Dropdown(id='comport_filtro',
	        options=[
	            {'label': 'Filtro pasa-bajas', 'value': 'pass_low'},
	            {'label': u'Filtro pasa-banda', 'value': 'pass_band'},
	            {'label': u'Filtro pasa-altas', 'value': 'pass_high'},

	        ],
	        value=' '
	    ),
	    html.Hr(),
	    html.H2(html.Button(id='button',n_clicks=0,children='Enter'),style={'textAlign':'center'}),
	    html.Hr(),
	    html.Div(id='tipo_fil'),
	    html.Hr(),
    	html.Div(id='comport_fil'),
    	html.Hr(),
    ]),
    html.Hr(),
    html.H3(html.Label('Señales de audio'),style={'textAlign':'center'}),
    dcc.Dropdown(id='num_audio',
        options=[
            {'label': 'Audio1', 'value': 'aud1'},
            {'label': u'Audio2', 'value': 'aud2'},
            {'label': u'Audio3', 'value': 'aud3'},

        ],
        value=' '
    ),
    html.Hr(),
    dcc.Graph(id='subir_audio'),
    html.H2(html.Button(id='button2',n_clicks=0,children='Graficar'),style={'textAlign':'center'}),
    html.Hr(),
    html.Div([
    html.H2(html.Button(id='button3',n_clicks=0,children='Reproducir'),style={'textAlign':'center'}),
    html.Div(id='sonido_orig')]),
    html.Hr(),
    html.Div([
    dcc.Graph(id='senal_filtrada'),
    html.H2(html.Button(id='button4',n_clicks=0,children='Filtrar'),style={'textAlign':'center'}),
    html.Hr(),
    html.Div([
    html.H2(html.Button(id='button5',n_clicks=0,children='Reproducir'),style={'textAlign':'center'}),
    html.Div(id='sonido_fil')]),
    ]),
   

])
#############################################################################

#################### MENU TIPO DE VENTANA A ESCOGER ##########################
# Se realiza el primer llamado a una funcion que discrimina si el filtro escogido
# es  FIR se muestra la lista desplegable del tipo de ventana que quiera escoger
# en caso de que sea IIR solo se inscribe mensaje que indica la eleccion, la cual es
#llamada cuando se presiona el primer enter.
@app.callback(
    dash.dependencies.Output('tipo_fil', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
	[dash.dependencies.State('tipo_filtro', 'value')]
)

def Menu_tipo_filtro(n_clicks,tipo):
	if tipo == 'FIR':
		return (
			html.H3(html.Label('Tipo de ventana'),style={'textAlign':'center'}),
	    	dcc.Dropdown(id='tip_win',
	        options=[
	            {'label': 'Flattop', 'value': 'flattop'},
	            {'label': u'Hann', 'value': 'hann'},
	            {'label': u'Hamming', 'value': 'hamming'},
	            {'label': u'Blackman', 'value': 'blackman'},
	        ],
	        value=' '
	   		)
	    	)
	else:
		if tipo == 'IIR':	
			return (html.Div(style={'backgroundColor': colors['background']},children=[
					html.H3(children='Escogio Filtro IIR', style={
		  				'textAlign': 'center',
		   			 	'color': colors['text'],
					}),
					]),

			)
#####################################################################################################

###################### MENU CON COMPORTAMIENTO DEL FILTRO PASA-(BAJAS,BANDA,ALTAS)###################
# En esta seccion se encuentra las casillas para ingresar valores luego que se seleccion un comportamiento
# de filtro sea, pasa-bajas,altas, o bandas y se discrimina igualmente por tipo de filtro si es IIR o FIR 
# para que vaya a las funciones correspondientes en donde se diseña y grafica el filtro especifico seleccionado.
@app.callback(
    dash.dependencies.Output('comport_fil', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
	[dash.dependencies.State('comport_filtro','value'),dash.dependencies.State('tipo_filtro','value')]
)
def menu_comport_filtro(n_clicks,comport,tipo):

	if comport == 'pass_low':
		if tipo == 'FIR':	
			return(
				html.Div(children=[html.H3(html.Label('Parametros del filtro'),style={'textAlign':'center'}),
				html.Label('Frecuencia de corte pasa-bajas'),
				html.Div(dcc.Input(id='frec_corte', type='number', value=0)),
				html.Label('Ganancia'),
				html.Div(dcc.Input(id='ganancia', type='number', value=0)),
				html.Label('Orden'),
				html.Div(dcc.Input(id='orden', type='number', value=0)),
				html.Label('Frecuencia de muestreo(Almenos 7 veces mas grande que frecuencia de corte)'),
				html.Div(dcc.Input(id='frec_muestreo', type='number', value=0)),
				html.H2(html.Button(id='button1',n_clicks=0,children='Enter'),style={'textAlign':'center'}),	
					],style={
						'textAlign': 'center',
				 			'color': colors['text'],
					}
				),
				html.Div(id='fir_pasab'),
				dcc.Graph(id='fir_pasab'),
				html.Div(id='fir_pasab_fase'),
				dcc.Graph(id='fir_pasab_fase'),
			)
		else:
			if tipo == 'IIR':	
				return(
					html.Div(children=[html.H3(html.Label('Parametros del filtro'),style={'textAlign':'center'}),
					html.Label('Frecuencia de corte pasa-bajas'),
					html.Div(dcc.Input(id='frec_corte', type='number', value=0)),
					html.Label('Ganancia'),
					html.Div(dcc.Input(id='ganancia', type='number', value=0)),
					html.Label('Orden'),
					html.Div(dcc.Input(id='orden', type='number', value=0)),
					html.Label('Frecuencia de muestreo(Almenos 7 veces mas grande que frecuencia de corte)'),
					html.Div(dcc.Input(id='frec_muestreo', type='number', value=0)),
					html.H2(html.Button(id='button1',n_clicks=0,children='Enter'),style={'textAlign':'center'}),	
						],style={
							'textAlign': 'center',
					 			'color': colors['text'],
						}
					),
					html.Div(id='iir_pasab'),
					dcc.Graph(id='iir_pasab'),
					html.Div(id='iir_pasab_fase'),
					dcc.Graph(id='iir_pasab_fase'),
				)
	if comport == 'pass_band':
		if tipo == 'FIR':
			return(
				html.Div(children=[html.H3(html.Label('Parametros del filtro'),style={'textAlign':'center'}),
				html.Label('Frecuencia de corte inferior'),
				html.Div(dcc.Input(id='frec_corte_inf', type='number', value=0)),
				html.Label('Frecuencia de corte Superior'),
				html.Div(dcc.Input(id='frec_corte_sup', type='number', value=0)),
				html.Label('Orden'),
				html.Div(dcc.Input(id='orden', type='number', value=0)),
				html.Label('Frecuencia de muestreo(Almenos 7 veces mas grande que frecuencia de corte)'),
				html.Div(dcc.Input(id='frec_muestreo', type='number', value=0)),
				html.H2(html.Button(id='button1',n_clicks=0,children='Enter'),style={'textAlign':'center'}),		
					],style={
						'textAlign': 'center',
				 			'color': colors['text'],
					}
				),
				html.Div(id='fir_pasaband'),
				dcc.Graph(id='fir_pasaband'), 
				html.Div(id='fir_pasabanda_fase'),
				dcc.Graph(id='fir_pasabanda_fase'),
			)
		else:
			if tipo == 'IIR':
				return(
				html.Div(children=[html.H3(html.Label('Parametros del filtro'),style={'textAlign':'center'}),
				html.Label('Frecuencia de corte inferior'),
				html.Div(dcc.Input(id='frec_corte_inf', type='number', value=0)),
				html.Label('Frecuencia de corte Superior'),
				html.Div(dcc.Input(id='frec_corte_sup', type='number', value=0)),
				html.Label('Orden'),
				html.Div(dcc.Input(id='orden', type='number', value=0)),
				html.Label('Frecuencia de muestreo(Almenos 7 veces mas grande que frecuencia de corte)'),
				html.Div(dcc.Input(id='frec_muestreo', type='number', value=0)),
				html.H2(html.Button(id='button1',n_clicks=0,children='Enter'),style={'textAlign':'center'}),		
					],style={
						'textAlign': 'center',
				 			'color': colors['text'],
					}
				),
				html.Div(id='iir_pasaband'),
				dcc.Graph(id='iir_pasaband'), 
				html.Div(id='iir_pasaband_fase'),
				dcc.Graph(id='iir_pasaband_fase'),
			)

	if comport == 'pass_high':
		if tipo == 'FIR':
			return(
				html.Div(children=[html.H3(html.Label('Parametros del filtro'),style={'textAlign':'center'}),
				html.Label('Frecuencia de corte pasa-altas'),
				html.Div(dcc.Input(id='frec_corte', type='number', value=0)),
				html.Label('Ganancia'),
				html.Div(dcc.Input(id='ganancia', type='number', value=0)),
				html.Label('Orden'),
				html.Div(dcc.Input(id='orden', type='number', value=0)),
				html.Label('Frecuencia de muestreo(Almenos 7 veces mas grande que frecuencia de corte)'),
				html.Div(dcc.Input(id='frec_muestreo', type='number', value=0)),
				html.H2(html.Button(id='button1',n_clicks=0,children='Enter'),style={'textAlign':'center'}),	
					],style={
						'textAlign': 'center',
				 			'color': colors['text'],
					}
				), 
				html.Div(id='fir_pasalt'),
				dcc.Graph(id='fir_pasalt'), 
				html.Div(id='fir_pasalt_fase'),
				dcc.Graph(id='fir_pasalt_fase'),
			)
		else:
			if tipo == 'IIR':
				return(
				html.Div(children=[html.H3(html.Label('Parametros del filtro'),style={'textAlign':'center'}),
				html.Label('Frecuencia de corte pasa-altas'),
				html.Div(dcc.Input(id='frec_corte', type='number', value=0)),
				html.Label('Ganancia'),
				html.Div(dcc.Input(id='ganancia', type='number', value=0)),
				html.Label('Orden'),
				html.Div(dcc.Input(id='orden', type='number', value=0)),
				html.Label('Frecuencia de muestreo(Almenos 7 veces mas grande que frecuencia de corte)'),
				html.Div(dcc.Input(id='frec_muestreo', type='number', value=0)),
				html.H2(html.Button(id='button1',n_clicks=0,children='Enter'),style={'textAlign':'center'}),	
					],style={
						'textAlign': 'center',
				 			'color': colors['text'],
					}
				), 
				html.Div(id='iir_pasalt'),
				dcc.Graph(id='iir_pasalt'), 
				html.Div(id='iir_pasalt_fase'),
				dcc.Graph(id='iir_pasalt_fase'),
			)

######################################################################################################################

####################### DISEÑO DE FILTRO FIR PASABAJAS Y GRAFICA DE RESPUESTA EN FRECUENCIA ##########################
# Esta es la funcion correspondiente que se llama cuando se indica que el filtro sera un FIR pasa-bajas, se diseña el
# luego de que se ingresan los parametros del filtro en las casillas y se presiona el segundo enter, se normaliza 
# frecuencia de corte con frecuencia de muestreo y se utiliza la funcion de scipy.signal firwin la cual permite 
# implementar el filtro deseado dependiendo de la ventana que previamente se haya escogido y nos entrega la respuesta
# natural del filtro diseñado, con la funcion freqz tambien de scipy.signal se obtiene un vector de frecuencias 
# y la respuesta en frecuencia del filtro recibiendo como parametro la respuesta natural del mismo, finalmente se grafica
# dicha respuesta.
@app.callback(
	dash.dependencies.Output('fir_pasab','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value'),
	dash.dependencies.State('tipo_filtro','value'),dash.dependencies.State('tip_win','value')]
)

def fir_pasabajas(n_clicks,fc,gain,orden,fs,tipo,win):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	if win == 'flattop':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hann':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hamming':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'blackman':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	H = np.abs(H)
	xfilter=w/np.pi * (fs/2)
	yfilter=H
	return {
		'data': [
			{'x':xfilter, 'y':yfilter*gain , 'type': 'line', 'name': 'respuesta del filtro en frecuencia'},
			
		],
		'layout': {
			'title': 'Respuesta en frecuencia del Filtro FIR pasa-bajas',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }
#############################################################################################################################

################### DISEÑO FILTRO IIR PASA-BAJAS  Y GRAFICA DE RESPUESTA EN FRECUENCIA ######################################
# Aca se diseña el filtro cuando se seleccionan la opciones de IIR y pasa-bajas igualmente luego de ingresar los parametros
# requeridos y de presionado el segundo enter, se normaliza la frecuencia de corte y se utiliza la funcion de scipy iirfilter
# la cual nos devuelve los coeficientes de un filtro analogico correspondiente a los valores ingresados, y luego con la funcion
# bilinear tambien de scipy se convierten estos a los de un filtro digital, se utiliza la funcion freqs que igual que su corres-
# pondiente usada en los FIR freqz devuelve la respuesta en frecuenciadel filtro en este caso utilizando los coeficientes calculados
# anteriormente y finalmente se grafica el comportamiento del filtro.
@app.callback(
	dash.dependencies.Output('iir_pasab','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),dash.dependencies.State('tipo_filtro','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value')]
)
def iir_pasabajas(n_clicks,fc,gain,tipo,orden,fs):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	banalog,aanalog=sp.iirfilter(orden, wcn, rp=None, rs=None, btype='high',analog=False, output='ba')
	bdig,adig=sp.bilinear(banalog, aanalog, fs=fs)
	w,H=sp.freqs(bdig, adig, worN=1024, plot=None)
	H = np.abs(H)
	xfilter=w/np.pi * (fs/2)
	return {
		'data': [
			{'x':xfilter, 'y':H*gain , 'type': 'line', 'name': 'respuesta del filtro en frecuencia'},
			
		],
		'layout': {
			'title': 'Respuesta en frecuencia del Filtro IIR pasa-bajas',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }

############################################################################################################

############### DISEÑO FILTRO FIR PASA-ALTAS Y GRAFICA DE RESPUESTA EN FRECUENCIA ##########################
# Esta es la funcion correspondiente que se llama cuando se indica que el filtro sera un FIR pasa-altas, se diseña el
# luego de que se ingresan los parametros del filtro en las casillas y se presiona el segundo enter, se normaliza 
# frecuencia de corte con frecuencia de muestreo y se utiliza la funcion de scipy.signal firwin la cual permite 
# implementar el filtro deseado dependiendo de la ventana que previamente se haya escogido y nos entrega la respuesta
# natural del filtro diseñado, con la funcion freqz tambien de scipy.signal se obtiene un vector de frecuencias 
# y la respuesta en frecuencia del filtro recibiendo como parametro la respuesta natural del mismo, finalmente se grafica
# dicha respuesta.
@app.callback(
	dash.dependencies.Output('fir_pasalt','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value'),
	dash.dependencies.State('tipo_filtro','value'),dash.dependencies.State('tip_win','value')]
)
def fir_pasaaltas(n_clicks,fc,gain,orden,fs,tipo,win):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	if win == 'flattop':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hann':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hamming':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'blackman':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	H = np.abs(H)
	xfilter=w/np.pi * (fs/2)
	xfilterin=xfilter[::-1]
	yfilter=H
	return {
		'data': [
			{'x':xfilterin, 'y':yfilter*gain , 'type': 'line', 'name': 'respuesta del filtro'},
			
		],
		'layout': {
			'title': 'Respuesta en frecuencia del Filtro FIR pasa-altas',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
    	}
###########################################################################################################

####################### DISEÑO FILTRO IIR PASA-ALTAS  Y GRAFICA DE RESPUESTA EN FRECUENCIA ################
# Aca se diseña el filtro cuando se seleccionan la opciones de IIR y pasa-altas igualmente luego de ingresar los parametros
# requeridos y de presionado el segundo enter, se normaliza la frecuencia de corte y se utiliza la funcion de scipy iirfilter
# la cual nos devuelve los coeficientes de un filtro analogico correspondiente a los valores ingresados, y luego con la funcion
# bilinear tambien de scipy se convierten estos a los de un filtro digital, se utiliza la funcion freqs que igual que su corres-
# pondiente usada en los FIR freqz devuelve la respuesta en frecuenciadel filtro en este caso utilizando los coeficientes calculados
# anteriormente y finalmente se grafica el comportamiento del filtro.
@app.callback(
	dash.dependencies.Output('iir_pasalt','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value')]
)
def iir_pasaaltas(n_clicks,fc,gain,orden,fs):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	banalog,aanalog=sp.iirfilter(orden, wcn, rp=None, rs=None, btype='low',analog=False, output='ba')
	bdig,adig=sp.bilinear(banalog, aanalog, fs=fs)
	w,H=sp.freqs(bdig, adig, worN=1024, plot=None)
	H = np.abs(H)
	xfilter=w/np.pi * (fs/2)
	return {
		'data': [
			{'x':xfilter, 'y':H*gain , 'type': 'line', 'name': 'respuesta del filtro en frecuencia'},
			
		],
		'layout': {
			'title': 'Respuesta en frecuencia del Filtro IIR pasa-altas',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }
#########################################################################################################

######################## DISEÑO FILTRO FIR PASA-BANDAS Y GRAFICA DE RESPUESTA EN FRECUENCIA ##############
# Esta es la funcion correspondiente que se llama cuando se indica que el filtro sera un FIR pasa-banda, se diseña el
# luego de que se ingresan los parametros del filtro en las casillas y se presiona el segundo enter, se normaliza 
# frecuencia de corte con frecuencia de muestreo y se utiliza la funcion de scipy.signal firwin la cual permite 
# implementar el filtro deseado dependiendo de la ventana que previamente se haya escogido y nos entrega la respuesta
# natural del filtro diseñado, con la funcion freqz tambien de scipy.signal se obtiene un vector de frecuencias 
# y la respuesta en frecuencia del filtro recibiendo como parametro la respuesta natural del mismo, finalmente se grafica
# dicha respuesta.
@app.callback(
	dash.dependencies.Output('fir_pasaband','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte_inf','value'),dash.dependencies.State('frec_corte_sup','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value'),
	dash.dependencies.State('tipo_filtro','value'),dash.dependencies.State('tip_win','value')]
)
def fir_pasabanda(n_clicks,fc1,fc2,orden,fs,tipo,win):
	global h
	orden=int(orden)
	fc1=float(fc1)
	fc2=float(fc2)
	fs=float(fs)
	h=[] 
	wcn1=np.pi*fc1/(fs/2) 
	wcn2=np.pi*fc2/(fs/2) 
	if win == 'flattop':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	if win == 'hann':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	if win == 'hamming':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	if win == 'blackman':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	H1 = np.abs(H1)
	xfilter1=w1/np.pi * (fs/2)
	yfilter1=H1
	return {
		'data': [
			{'x':xfilter1, 'y':-yfilter1, 'type': 'line', 'name': 'respuesta del filtro'},
			
		],
		'layout': {
			'title': 'Respuesta en frecuencia del Filtro FIR pasa-banda',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
    	}
#######################################################################################################

########################### RESPUESTA EN FRECUENCIA FILTRO IIR PASA-BANDA #############################
# Aca se diseña el filtro cuando se seleccionan la opciones de IIR y pasa-bandaigualmente luego de ingresar los parametros
# requeridos y de presionado el segundo enter, se normaliza la frecuencia de corte y se utiliza la funcion de scipy iirfilter
# la cual nos devuelve los coeficientes de un filtro analogico correspondiente a los valores ingresados, y luego con la funcion
# bilinear tambien de scipy se convierten estos a los de un filtro digital, se utiliza la funcion freqs que igual que su corres-
# pondiente usada en los FIR freqz devuelve la respuesta en frecuenciadel filtro en este caso utilizando los coeficientes calculados
# anteriormente y finalmente se grafica el comportamiento del filtro.
@app.callback(
	dash.dependencies.Output('iir_pasaband','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte_inf','value'),dash.dependencies.State('frec_corte_sup','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value')]
)
def iir_pasabanda(n_clicks,fc1,fc2,orden,fs):
	global h
	orden=int(orden)
	fc1=float(fc1)
	fc2=float(fc2)
	fs=float(fs)
	h=[] 
	wcn1=np.pi*fc1/(fs/2)
	wcn2=np.pi*fc2/(fs/2)
	b,a=sp.iirfilter(orden, [wcn1,wcn2], rp=None, rs=None, btype='bandpass',analog=True, output='ba')
	w,H=sp.freqs(b, a, worN=1024, plot=None)
	H = np.abs(H)
	xfilter1=w/np.pi * (fs/2)
	return {
		'data': [
			{'x':xfilter1, 'y':H , 'type': 'line', 'name': 'respuesta del filtro en frecuencia'},
			
		],
		'layout': {
			'title': 'Respuesta en frecuencia del Filtro IIR pasa-banda',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }

#######################################################################################################

###########################	RESPUESTA EN FASE FILTRO FIR PASA BAJAS ###################################
# Esta funcion es utilizada cuando se sabe que se eligio un filtro FIR pasa-bajas para graficar su 
# respuesta en fase, a diferencia de lo que se realiza graficando la respuesta en frecuencia aca se utilizan
# las funciones angle y fftshift ambas de numpy para hallar el comportamiento en fase de la respuesta
# en frecuencia previamente calculada.
@app.callback(
	dash.dependencies.Output('fir_pasab_fase','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value'),
	dash.dependencies.State('tipo_filtro','value'),dash.dependencies.State('tip_win','value')]
)

def fir_pasabajas_fase(n_clicks,fc,gain,orden,fs,tipo,win):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	if win == 'flattop':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hann':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hamming':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'blackman':
		h=sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	H = np.abs(H)

	xfas=(w-np.pi)*fs/(2*np.pi)
	yfas=np.angle(np.fft.fftshift(H))
	return {
        'data': [
				{'x':xfas,'y':yfas, 'type': 'line', 'name': 'respuesta del filtro en fase'},
				
			],
			'layout': {
				'title': 'Respuesta en fase del Filtro FIR pasa-bajas',
				'plot_bgcolor': colors['graf'],
				'paper_bgcolor': colors['background'],
				'font': {
					'color': colors['text']
        		}
        	}
        }
##############################################################################################

########################### RESPUESTA EN FASE IIR PASA-BAJAS  ###################################
# Esta funcion es utilizada cuando se sabe que se eligio un filtro IIR pasa-bajas para graficar su 
# respuesta en fase, ademas de lo que se realiza graficando la respuesta en frecuencia aca se utilizan
# las funciones angle y fftshift ambas de numpy para hallar el comportamiento en fase de la respuesta
# en frecuencia previamente calculada.

@app.callback(
	dash.dependencies.Output('iir_pasab_fase','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),dash.dependencies.State('tipo_filtro','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value')]
)
def iir_pasabajas_fase(n_clicks,fc,gain,tipo,orden,fs):
	global h
	#if tipo == 'IIR':
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	banalog,aanalog=sp.iirfilter(orden, wcn, rp=None, rs=None, btype='high',analog=False, output='ba')
	bdig,adig=sp.bilinear(banalog, aanalog, fs=fs)
	w,H=sp.freqs(bdig, adig, worN=1024, plot=None)
	H = np.abs(H)
	H1=np.angle(np.fft.fftshift(H))
	return {
		'data': [
			{'x':w, 'y':H1 , 'type': 'line', 'name': 'respuesta del filtro en frecuencia'},
			
		],
		'layout': {
			'title': 'Respuesta en fase del Filtro IIR pasa-bajas',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }


################################################################################################

###################### RESPUESTA EN FASE FILTRO FIR PASA ALTAS#################################
# Esta funcion es utilizada cuando se sabe que se eligio un filtro FIR pasa-altas para graficar su 
# respuesta en fase, ademas de lo que se realiza graficando la respuesta en frecuencia aca se utilizan
# las funciones angle y fftshift ambas de numpy para hallar el comportamiento en fase de la respuesta
# en frecuencia previamente calculada.
@app.callback(
	dash.dependencies.Output('fir_pasalt_fase','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value'),
	dash.dependencies.State('tipo_filtro','value'),dash.dependencies.State('tip_win','value')]
)
def fir_pasaaltas_fase(n_clicks,fc,gain,orden,fs,tipo,win):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	if win == 'flattop':
		h=-sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hann':
		h=-sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'hamming':
		h=-sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	if win == 'blackman':
		h=-sp.firwin(orden+1,wcn,width=None,window=win,pass_zero=True)
		w, H = sp.freqz(h, worN=1024)
	H = np.abs(H)

	xfas=(w-np.pi)*fs/(2*np.pi)
	yfas=np.angle(np.fft.fftshift(H)) 
	return {
        'data': [
				{'x':xfas,'y':yfas, 'type': 'line', 'name': 'respuesta del filtro en fase'},
				
			],
			'layout': {
				'title': 'Respuesta en fase del Filtro FIR pasa-altas',
				'plot_bgcolor': colors['graf'],
				'paper_bgcolor': colors['background'],
				'font': {
					'color': colors['text']
        		}
        	}
        }
###########################################################################################

##################### RESPUESTA EN FASE FILTRO IIR PASA-ALTAS###############################
# Esta funcion es utilizada cuando se sabe que se eligio un filtro IIR pasa-altas para graficar su 
# respuesta en fase, ademas de lo que se realiza graficando la respuesta en frecuencia aca se utilizan
# las funciones angle y fftshift ambas de numpy para hallar el comportamiento en fase de la respuesta
# en frecuencia previamente calculada.

@app.callback(
	dash.dependencies.Output('iir_pasalt_fase','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte','value'),dash.dependencies.State('ganancia','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value')]
)
def iir_pasaaltas_fase(n_clicks,fc,gain,orden,fs):
	global h
	orden=int(orden)
	fc=float(fc)
	fs=float(fs)
	gain=float(gain)
	h=[] 
	wcn=np.pi*fc/(fs/2)
	banalog,aanalog=sp.iirfilter(orden, wcn, rp=None, rs=None, btype='low',analog=False, output='ba')
	bdig,adig=sp.bilinear(banalog, aanalog, fs=fs)
	w,H=sp.freqs(bdig, adig, worN=1024, plot=None)
	H = np.abs(H)
	H1=np.angle(np.fft.fftshift(H))
	return {
		'data': [
			{'x':w, 'y':H1 , 'type': 'line', 'name': 'respuesta del filtro en fase'},
			
		],
		'layout': {
			'title': 'Respuesta en fase del Filtro IIR pasa-altas',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }

############################################################################################

################### RESPUESTA EN FASE FILTRO FIR PASA BANDA ################################
# Esta funcion es utilizada cuando se sabe que se eligio un filtro FIR pasa-banda para graficar su 
# respuesta en fase, ademas de lo que se realiza graficando la respuesta en frecuencia aca se utilizan
# las funciones angle y fftshift ambas de numpy para hallar el comportamiento en fase de la respuesta
# en frecuencia previamente calculada.
@app.callback(
	dash.dependencies.Output('fir_pasabanda_fase','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte_inf','value'),dash.dependencies.State('frec_corte_sup','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value'),
	dash.dependencies.State('tipo_filtro','value'),dash.dependencies.State('tip_win','value')]
)
def fir_pasabanda_fase(n_clicks,fc1,fc2,orden,fs,tipo,win):
	global h
	orden=int(orden)
	fc1=float(fc1)
	fc2=float(fc2)
	fs=float(fs)
	h=[] 
	wcn1=np.pi*fc1/(fs/2) 
	wcn2=np.pi*fc2/(fs/2)
	if win == 'flattop':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	if win == 'hann':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	if win == 'hamming':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	if win == 'blackman':
		h1=sp.firwin(orden+1,[wcn1,wcn2],width=None,window=win,pass_zero=True)
		w1, H1 = sp.freqz(h1, worN=1024)
	H1 = np.abs(H1)
	xfas=(w1-np.pi)*fs/(2*np.pi)
	yfas=np.angle(np.fft.fftshift(H1))
	return {
		'data': [
			{'x':xfas, 'y':yfas, 'type': 'line', 'name': 'respuesta del filtro'},
			
		],
		'layout': {
			'title': 'Respuesta en fase del Filtro FIR pasa-banda',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
    	}
####################################################################################################

########################## RESPUESTA EN FASE FILTRO IIR PASA-BANDA ###################################
# Esta funcion es utilizada cuando se sabe que se eligio un filtro IIR pasa-banda para graficar su 
# respuesta en fase, ademas de lo que se realiza graficando la respuesta en frecuencia aca se utilizan
# las funciones angle y fftshift ambas de numpy para hallar el comportamiento en fase de la respuesta
# en frecuencia previamente calculada.
@app.callback(
	dash.dependencies.Output('iir_pasaband_fase','figure'),
	[dash.dependencies.Input('button1','n_clicks')],
	[dash.dependencies.State('frec_corte_inf','value'),dash.dependencies.State('frec_corte_sup','value'),
	dash.dependencies.State('orden','value'),dash.dependencies.State('frec_muestreo','value')]
)
def iir_pasabanda_fase(n_clicks,fc1,fc2,orden,fs):
	global h
	orden=int(orden)
	fc1=float(fc1)
	fc2=float(fc2)
	fs=float(fs)
	h=[] 
	wcn1=np.pi*fc1/(fs/2)
	wcn2=np.pi*fc2/(fs/2)
	b,a=sp.iirfilter(orden, [wcn1,wcn2], rp=None, rs=None, btype='bandpass',analog=True, output='ba')
	w,H=sp.freqs(b, a, worN=1024, plot=None)
	H = np.abs(H)
	H1=np.angle(np.fft.fftshift(H))
	return {
		'data': [
			{'x':w, 'y':H1 , 'type': 'line', 'name': 'respuesta del filtro en fase'},
			
		],
		'layout': {
			'title': 'Respuesta en fase del Filtro IIR pasa-banda',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
     }
#######################################################################################################################

####################### SEÑALES DE AUDIO ###################################################
@app.callback(
	dash.dependencies.Output('subir_audio','figure'),
	[dash.dependencies.Input('button2','n_clicks')],
	[dash.dependencies.State('num_audio','value')]
)
def Graf_audio(n_clicks,opc):
	global nombre
	sig=[]
	nombre = '' 
	if opc == 'aud1':
		fs_sig,sig=read('aud_1.wav')
		nombre='aud_1.wav'
	if opc == 'aud2':
		fs_sig,sig=read('aud_2.wav')
		nombre='aud_2.wav'
	if opc == 'aud3':
		fs_sig,sig=read('aud_3.wav')
		nombre='aud_3.wav'
	sig=((sig-np.mean(sig))/float(max(abs(sig))))
	t=np.arange(len(sig))
	return {
				'data': [{'x': t, 'y': sig}],
				'layout': {
			'title': 'Audio original normalizado',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
	 }

@app.callback(
	dash.dependencies.Output('sonido_orig','children'),
	[dash.dependencies.Input('button3','n_clicks')]
)
def reproducir(n_clicks):
	global nombre
	ws.PlaySound(nombre,ws.SND_ASYNC | ws.SND_ALIAS)
@app.callback(
	dash.dependencies.Output('senal_filtrada','figure'),
	[dash.dependencies.Input('button4','n_clicks')],
	[dash.dependencies.State('num_audio','value')]
)
def senal_fil(n_clicks,opc):
	global h,salida
	fs_sig,senal=read(nombre)
	senal_fil=[]
	senal_fil=np.convolve(senal,h,mode='same')
	sal1=sal=(senal_fil-np.mean(senal_fil))/float(max(abs(senal_fil)))
	sal = 100000*sal1/np.max(sal1)
	sal= sal.astype(np.int16)
	write('audiofil.wav',fs_sig,sal)
	salida='audiofil.wav'
	t=np.arange(len(sal1))
	return {
				'data': [{'x': t, 'y': sal1}],
				'layout': {
			'title': 'Audio original normalizado',
			'plot_bgcolor': colors['graf'],
			'paper_bgcolor': colors['background'],
			'font': {
				'color': colors['text']
			}
		}
	 }
@app.callback(
	dash.dependencies.Output('sonido_fil','children'),
	[dash.dependencies.Input('button5','n_clicks')]
	)
def reproducir_fil(n_clicks):
	global salida
	ws.PlaySound(salida,ws.SND_ASYNC | ws.SND_ALIAS)
############################################################################################
#################### PARA REINICIAR EL PROGRAMA CUANDO ESTA CORRIENDO Y SE GUARDAN LOS CAMBIOS EN EL EDITOR ###########
if __name__ == '__main__':
    app.run_server(debug=True)

#######################################################################################################################