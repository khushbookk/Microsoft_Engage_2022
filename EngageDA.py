

from sqlalchemy import create_engine, inspect
import pandas as pd
import streamlit as st
import time
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

st.set_page_config()
# host=st.secrets.local.mysql["host"]
# port = st.secrets.local.mysql["port"]
# database=st.secrets.local.mysql["database"]
# user=st.secrets.local.mysql["username"]
# password=st.secrets.local.mysql["password"]

host=st.secrets.connections.mysql["host"]
port = st.secrets.connections.mysql["port"]
database=st.secrets.connections.mysql["database"]
user=st.secrets.connections.mysql["username"]
password=st.secrets.connections.mysql["password"]

# PYTHON FUNCTION TO CONNECT TO THE MYSQL DATABASE AND
# RETURN THE SQLACHEMY ENGINE OBJECT
def get_connection():
	return create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(user,password,host,port,database))


def define_dashboard_config():
	st.set_page_config(
		layout="wide",  
		initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
		page_title='Automotive Data Analysis', 
		page_icon=None,  
	)

	col_1, col_2 = st.columns([3,1])
	# with col_1:
	# 	st.title('Automotive Data Analysis')
	with col_2:
		st.text(time.strftime("%Y-%m-%d %H:%M"))



def load_image():

	col_1, col_2 = st.columns([2,2])
	with col_1:
		image = Image.open(r"Image/lux.png")
		st.image(image, use_column_width = 'auto' )
	with col_2:
		image = Image.open(r"Image/Automo.png")
		st.image(image, use_column_width = 'auto' )


def about(conn):
	query1='select * from basic_table limit 10; '
	query2='select * from sales_table limit 10; '
	query3='select * from price_table limit 10; '

	basic_table=pd.read_sql_query(query1,conn)
	sales_table=pd.read_sql_query(query2,conn)
	price_table=pd.read_sql_query(query3,conn)

	st.write("Automotive Data Analysis - Consumer analytics")
	st.write('''
			The data analysis is based on DVM-Car dataset, a UK automotive market based research dataset 
			created for business analytics and applications purposes.
			
			I have made use of 'Basic table', 'Sales table', 'Price table' from the dataset to depict
			consumer analytics and sales modelling.
			''')
	st.write('''
			Basic Table : This table is mainly for indexing other tables. It includes 1,011 generic models 
			from 101 automakers.''')
	st.write(basic_table)
	st.write('''
			Sales Table : It contains 20 years car sales data of the UK market(based on the government 
			released statics of new car registrations).In sum, it covers the sales of 773 car models from 
			2001 to 2020.''')
	st.write(sales_table)
	st.write('''
			Price Table : This table contains the entry-level (i.e.,the cheapest trim price) new car 
			prices of 647 models across years.''')
	st.write(price_table)
	st.markdown("***")
	st.write("Dataset Reference")
	st.write('''Jingming Huang, Bowei Chen, Lan Luo, Shigang Yue, Iadh Ounis (2021). 
			"DVM-CAR: A large-scale automotive dataset for visual marketing research and applications". 
			In: ArXiv e-prints (Aug.2021). arXiv: 2109.00881''')


def automaker_models(conn):

	st.write('''
			Pie-chart having each wedge denoting the number of models produced by different Automakers. 
			''')
	sql_query ='''select Automaker, count(*) as count from basic_table group by Automaker 
				  having count(*) > 2 order by count desc;'''

	sql_query2 ='''select Automaker, count(*) as count from basic_table group by Automaker 
				  having count(*) < 3 order by count desc;'''

	df = pd.read_sql_query(sql_query, conn)
	df2 = pd.read_sql_query(sql_query2,conn)

	col0=df.columns[0]
	col1=df.columns[1]
	
	other_automakers_count = len(df2['Automaker'])
	other_automakers_models_count = sum(df2['count'])

	# st.write(other_automakers_count,other_automakers_models_count)

	# Creating plot
	fig = plt.figure(figsize =(10, 7))
  

	explode_list= [0] * len(df[col0])
	explode_list.append(0.2)
	automakers=list(df[col0])
	automakers.append('other {} automakers'.format(other_automakers_count))
	model_count=list(df[col1])
	model_count.append(other_automakers_models_count)
	plt.pie(model_count,labels=automakers,radius=2.2, labeldistance=1.01, rotatelabels = True, 
	startangle = 0 ,textprops=dict(fontsize= 10,va= "center",  rotation_mode= 'anchor'),
	 explode=explode_list)
	st.write(fig) 
	st.write("List of other 38 Automakers :")
	st.write(df2['Automaker'])

def sales_analysis(conn):

	st.write('''
			Bar plot of sales of different models of an Automaker across 20 years.
			This plot will help in year-wise analysis for sales of a model. 
			''')

	query = "select distinct Maker from sales_table;"
	df = pd.read_sql_query(query, conn)
	# st.write(df)
	menu1 = list(df['Maker'])
	choice2 = st.selectbox("Select Automaker",menu1)
	query2= 'select Genmodel from sales_table where Maker="{}";'.format(choice2)
	df2 = pd.read_sql_query(query2, conn)
	# st.write(df2)
	menu2 = list(df2['Genmodel'])
	choice3 = st.selectbox("Select Model",menu2)

	query3= 'select * from sales_table where Maker="{}" and Genmodel = "{}";'.format(choice2,choice3)
	df3 = pd.read_sql_query(query3, conn)


	# creating the bar plot
	years= df3.columns[3:].tolist()
	x_labels=years
	values = (list(df3.iloc[0]))[3:] 
	fig = plt.figure(figsize = (10, 5))
	plt.bar(x_labels, values, color=(0.5, 0.4, 0.4),  edgecolor='white',
			width = 0.4)
	plt.xticks(rotation=30, ha='right')
	plt.xlabel("Years")
	plt.ylabel("Sales")
	plt.title("Sales Analysis")
	st.write(fig) 


def automaker_sales(conn):

	st.write('''
			Comparative Analysis for sales of different Automakers.
			''')
	
	query1='''select Maker, sum(`2020`) as `2020`, sum(`2019`) as `2019`, sum(`2018`) as `2018`, sum(`2017`) as `2017`, sum(`2016`) as `2016`,
			sum(`2015`) as `2015`, sum(`2014`) as `2014`, sum(`2013`) as `2013`, sum(`2012`) as `2012`, sum(`2011`) as `2011`,
			sum(`2010`) as `2010`, sum(`2009`) as `2009`, sum(`2008`) as `2008`, sum(`2007`) as `2007`, sum(`2006`) as `2006`, 
			sum(`2005`) as `2005`, sum(`2004`) as `2004`, sum(`2003`) as `2003`, sum(`2002`) as `2002`, sum(`2001`) as `2001` 
			from sales_table group by Maker;'''
	df1 = pd.read_sql_query(query1, conn)
	automaker_list=list(df1.iloc[:,0])

	options = st.multiselect('Select Automakers',automaker_list)

	if(options):

		year_list=list(range(2001,2021))[::-1] #list [2020,2019.....2001]

		df2=pd.DataFrame({'Year' : year_list})
		# st.write(df2)

		c=0
		for i in automaker_list:
			automaker_sales=list(df1.iloc[c,1:] )
			df3=pd.DataFrame( { i : automaker_sales } )
			df2=df2.join(df3)
			c+=1

		# st.write(df2)
		c=0
		fig = plt.figure(figsize = (10,5))
		
		for i in options:
			plt.plot(df2['Year'], df2[i], label=i)
			

		plt.xticks(ticks=df2['Year'], labels=df2['Year'], rotation =30)

		plt.xlabel('Year')
		plt.ylabel('Sales')

		plt.title('Comparative Sales Analysis of different Models')

		plt.legend()
		# plt.show()
		st.write(fig)

def popular_model_automaker(conn):

	st.write('''
			Popular models of an Automaker company based on highest sales amongst all models in span of 20 years.
			''')

	query = 'select distinct Maker from sales_table;'
	df = pd.read_sql_query(query, conn)
	# st.write(df)
	menu = list(df['Maker'])
	choice = st.selectbox("Select Automaker",menu)
	query2 = '''select Genmodel, `2020`+`2019`+`2018`+`2017`
			+`2016`+`2015`+`2014`+`2013`+`2012`+`2011`+`2010`+`2009`+`2008`+`2007`
			+`2006`+`2005`+`2004`+`2003`+`2002`+`2001` as total_sales_count from sales_table
			where Maker="{}";'''.format(choice)
	df2=pd.read_sql_query(query2, conn)
	#st.write(df2)

	y=df2['Genmodel']
	x=df2['total_sales_count']
	fig = plt.figure() #figsize = (10,5)
	plt.tight_layout();
	plt.barh(y, x)

	plt.xticks(fontsize=7)
	plt.yticks(fontsize=7)
	# setting label of y-axis
	plt.ylabel("Genmodel")

	# setting label of x-axis
	plt.xlabel("Sales Count")
	plt.title("Popularity Analysis")
	st.write(fig)

def price_sales(conn):

	st.write('''
			Comparision between price and sales trend of an Automaker model across 20 years
			''')

	query = '''select distinct Maker from price_table where (upper(Maker),Genmodel_ID) in 
				(select distinct Maker,Genmodel_ID from sales_table);'''
	df = pd.read_sql_query(query, conn)
	# st.write(df)
	menu1 = list(df['Maker'])
	choice1 = st.selectbox("Select Automaker",menu1)
	query2= '''select distinct Genmodel from price_table where upper(Maker)="{}" and (upper(Maker),Genmodel_ID) in 
			(select distinct Maker,Genmodel_ID from sales_table);'''.format(choice1)
	df2 = pd.read_sql_query(query2, conn)
	# st.write(df2)

	menu2 = list(df2['Genmodel'])
	choice2 = st.selectbox("Select Model",menu2)


	#In some cases  Genmodel names in price_table are not exactly similar to sales_table
	# therefore fetching Genmodel_ID
	query3= 'select distinct Genmodel_ID from price_table where Maker="{}" and Genmodel="{}";'.format(choice1,choice2)
	df3 = pd.read_sql_query(query3, conn)
	Genmodel_ID=df3.iat[0,0]

	query4='select * from price_table where Maker="{}" and Genmodel_ID="{}";'.format(choice1,Genmodel_ID)
	df4 = pd.read_sql_query(query4, conn)

	query5='select * from sales_table where Maker=upper("{}") and Genmodel_ID="{}";'.format(choice1,Genmodel_ID)
	df5 = pd.read_sql_query(query5, conn)

	years=np.arange(2001,2021,1)

	df6 = pd.DataFrame({'Year' : years},index=years)
	entry_price=list(df4['Entry_price'])
	years_price_index=list(df4['Year'])
	# st.write(years_price_index)
	df6 = df6.join(pd.DataFrame({'Entry Price':entry_price},index=years_price_index) )
	sales = list(df5.iloc[0,3:])[::-1] #reversed list
	df6 = df6.join(pd.DataFrame({'Sales':sales},index=years) )
	df6=df6.fillna(0)  #fill NA values 0

	fig, axs = plt.subplots(2)
	fig.suptitle('Sales-Price')

	axs[0].plot(list(df6['Year']), list(df6['Entry Price']))
	axs[1].plot(list(df6['Year']), list(df6['Sales']))

	axs[0].set_xticks(list(df6['Year']))
	axs[0].set_xticklabels(list(df6['Year']), fontsize=7)
	plt.setp(axs[0].get_xticklabels(), rotation=45)

	axs[1].set_xticks(list(df6['Year']))
	axs[1].set_xticklabels(list(df6['Year']), fontsize=7)
	plt.setp(axs[1].get_xticklabels(), rotation=45)

	axs[0].set_xlabel('Year')
	axs[1].set_xlabel('Year')
	axs[0].set_ylabel('Entry price')
	axs[1].set_ylabel('Sales')

	fig.tight_layout()
	st.write(fig)
	



def main():
	try:	
		# GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
		conn = get_connection()

	except Exception as ex:
		print("Connection could not be made due to the following error: \n", ex)
	
	# plt.style.use('dark_background')

	define_dashboard_config()


	menu = ["Automotives Data Analysis", "About", "Automaker-Models", "Automaker-Models-Sales", "Automaker-sales",
	 "Popular-Model-Automaker", "Price-Sales"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice=="Automotives Data Analysis":
		st.title('Automotive Data Analysis')
		load_image()

	elif choice == "About":
		st.header('About')
		about(conn)

	elif choice == "Automaker-Models":
		st.header("Automaker Model Analysis")
		automaker_models(conn)

	elif choice == "Automaker-Models-Sales" :
		st.header("Automaker Model Sales")
		sales_analysis(conn)
	
	elif choice == "Automaker-sales" :
		st.header("Automaker Sales")
		automaker_sales(conn)
	
	elif choice == "Popular-Model-Automaker" :
		st.header("Popular Model Automaker")
		popular_model_automaker(conn)
	
	elif choice == "Price-Sales" :
		st.header("Price Sales")
		price_sales(conn) 

	
main()    
