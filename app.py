# Imports
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Load data
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

# Data cleaning
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.sex = gss_clean.sex.replace({'female': 'women', 'male': 'men'})
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
         
# This is the text
markdown_text = '''There is a gender wage gap in the United States. As of 2020, women earn 82 cents for every dollar a man earns, according to data from the Bureau of Labor Statistics. [This is in part due to historical funneling of women into unpaid or low-pay caregiver roles and men into higher-pay trades such as construction](https://americanprogress.org/article/quick-facts-gender-wage-gap/). While efforts such as increase educational attainment by women have closed the gap (the gap has closed by 4 cents in over a decade), more work needs to be done. [Women still earn less than men in nearly all occupations and women earn less than their same race and ethnicity counterpart at every level of educational attainment](https://blog.dol.gov/2021/03/19/5-facts-about-the-state-of-the-gender-pay-gap), according to the Department of Labor Blog. 

The General Social Survey (GSS) has surveyed adults in the United States since 1972. According to the GSS website, the survey collects data on contemporary American society in order to monitor and explain trends in opinions, attitudes and behaviors. Our dataset contains demographics and attitudes about gender roles and income. For an example of how the GSS measures variables such as Occupational Prestige, please see [methodology](http://gss.norc.org/Documents/reports/methodological-reports/MR122%20Occupational%20Prestige.pdf). For a list of questions asked such as "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family", please see [codebook](http://www.gss.norc.org/Documents/codebook/GSS%202021%20Codebook%20R1.pdf).
'''

# This is the table 
## that shows the mean income, occupational prestige, socioeconomic index, and years of education for men and for women
mydata =  gss_clean.groupby('sex').agg({'education': 'mean', 
                                        'job_prestige': 'mean',
                                        'socioeconomic_index': 'mean',
                                        'income': 'mean'}).round(2).reset_index()\
                        .rename({'sex':'Gender',
                             'income': 'Mean Income', 
                             'job_prestige': 'Mean Job Prestige Score',
                             'socioeconomic_index': 'Mean Socioeconomic Index',
                             'education': 'Mean Years of Education'}, axis = 1)
## web-enabled version of this table
table = ff.create_table(mydata) 

# This is the interactive scatterplot
fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', color = 'sex', trendline='ols',
                labels={'job_prestige':'Job Prestige Score','income':'Income'},
                hover_data=['education', 'socioeconomic_index'])


# This is the interactive box plot for income 
fig_box1 = px.box(gss_clean, x = 'sex', y = 'income', color = 'sex', 
             labels = {'income':'Income', 'sex': ''})
fig_box1.update_layout(showlegend=False)


# This is the interactive box plot for job_prestige
fig_box2 = px.box(gss_clean, x = 'sex', y = 'job_prestige', color = 'sex', 
             labels = {'job_prestige':'Job Prestige Score', 'sex': ''})
fig_box2.update_layout(showlegend=False)


# This is the interactive facet grid
## Create a new dataframe 
mydata = gss_clean[['income', 'sex', 'job_prestige']]
## Create new features that breaks job_prestige into six categories with equally sized ranges
mydata['job_prestige_binned'] = pd.cut(mydata.job_prestige, 6)
## Reorder the bins 
# mydata.job_prestige_binned = mydata.job_prestige_binned.astype('str').astype('category').cat.reorder_categories(['(15.936, 26.667]',
#                                                                                                                  '(26.667, 37.333]',
#                                                                                                                  '(37.333, 48.0]',
#                                                                                                                  '(48.0, 58.667]',
#                                                                                                                  '(58.667, 69.333]',
#                                                                                                                  '(69.333, 80.0]'])
## Reorder the bins 
mydata.job_prestige_binned = mydata.job_prestige_binned.astype('str')
order = ['(15.936, 26.667]', '(26.667, 37.333]', '(37.333, 48.0]', '(48.0, 58.667]', '(58.667, 69.333]', '(69.333, 80.0]']
mydata.job_prestige_binned = mydata.job_prestige_binned.astype('category').cat.reorder_categories(order)

## Drop rows with missing data
mydata = mydata.dropna()
## Create a facet grid with 3 rows and 2 columns 
fig_facet = px.box(mydata, x = 'sex', y = 'income', color = 'sex', 
             labels = {'income':'Income', 'sex': ''}, 
             facet_col = 'job_prestige_binned', facet_col_wrap = 2,
             color_discrete_map = {'men':'blue', 'women':'red'}, 
             category_orders={'job_prestige_binned': ['(15.936, 26.667]',
                                                            '(26.667, 37.333]',
                                                            '(37.333, 48.0]',
                                                            '(48.0, 58.667]',
                                                            '(58.667, 69.333]',
                                                            '(69.333, 80.0]']}, height=1500)
fig_facet.for_each_annotation(lambda a: a.update(text=a.text.replace("job_prestige_binned=", "Job Prestige = ")))



# Code for app
display = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
groupby = ['sex', 'region', 'education']

##app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    [
        ## Add a descriptive title
        html.H2("Exploring Attitudes about Gender and Income as measured by the General Social Survey (GSS)"),
        
        ## Add the markdown text you wrote in problem 1
        dcc.Markdown(children = markdown_text),
        
        ## Add the table you made in problem 2
        ## And add subtitles for all subsequent graphs
        html.H3("Mean values for Education, Occupational Prestige, Socioeconomic Index, and Income for Men and Women"),
        dcc.Graph(figure=table),
        
        ## Alter the barplot from problem 3 to include user inputs
        html.Div([            
            # The first drop down menu
            html.H3("Display:"),
            dcc.Dropdown(id ='display',
                options=[{'label': i, 'value': i} for i in display],
                value ='male_breadwinner'),
            # The second drop down menu
            html.H3("Groupby:"),
            dcc.Dropdown(id ='groupby',
                options =[{'label': i, 'value': i} for i in groupby],
                value ='sex'),
        ], style ={'width': '25%', 'float': 'left', 'height': 800}),  
        
        html.Div([
            dcc.Graph(id="graph")
        ], style ={'width': '70%', 'float': 'right', 'height': 800}),
        
        ## Add the scatterplot you made in problem 4
        html.H3("Occupational Prestige vs. Income for Men and Women"),
        dcc.Graph(figure=fig_scatter),
    
        ## Add the two boxplots you made in problem 5 side-by-side
        html.Div([
            html.H3("Distribution of Income by Gender"),
            dcc.Graph(figure = fig_box1)
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            html.H3("Distribution of Occupational Prestige by Gender"),
            dcc.Graph(figure = fig_box2)
        ], style = {'width':'48%', 'float':'right'}),
    
        ## Add the faceted boxplots you made in problem 6
        html.H3("Distribution of Income for Varying Occupational Prestige by Gender"),
        dcc.Graph(figure=fig_facet)
    ]
)

## Requisite callback block for user-input graph
@app.callback(Output(component_id="graph",component_property="figure"), 
             [Input(component_id='display',component_property="value"),
              Input(component_id='groupby',component_property="value")])        

## Dictate the type of graph for user-input graph
def make_figure(display, groupby):
    return px.bar(gss_clean.groupby([groupby, display]).size().to_frame(name = 'count').reset_index(), 
                 x = display, 
                 y = 'count',
                 color = groupby, 
                 barmode = 'group', 
                 text = 'count', 
                 height = 800)

if __name__ == '__main__':
    ##app.run_server(mode='inline', debug=True, port = 8053)
    app.run_server(debug=True)
