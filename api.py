from flask import Flask, render_template, request, abort, redirect, url_for
from wtforms import Form, StringField, validators
import sqlite3
from sqlite3 import Error

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

  

def execute_query(connection, query, values = ()):
    
    try:
        if len(values)> 0:
            connection.execute(query, (values,))
            
        else:
            connection.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
create_recipes_table = """
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        image TEXT NOT NULL,
        link TEXT NOT NULL
);
"""


   


app = Flask(__name__)

class CreateRecipeForm(Form):
    title = StringField('Recipe Title', [validators.Length(min=4, max=50)])
    image = StringField('Image Address', [validators.Length(min=10)])
    link = StringField('Link Address', [validators.Length(min=10)])

recipes = [
        {
            "title": "BBQ Sweet and Sour Chicken Wings",
            "image": "https://image.freepik.com/free-photo/chicken-wings-barbecue-sweetly-sour-sauce-picnic-summer-menu-tasty-food-top-view-flat-lay_2829-6471.jpg",
            "link": "https://cookpad.com/us/recipes/347447-easy-sweet-sour-bbq-chicken"
        },
        {
            "title": "Chicken Fettuccine Alfredo",
            "image": "https://image.freepik.com/free-photo/fettucine-white-cream-sauce-with-shrimp-mushroom_74190-5969.jpg",
            "link": "https://www.foodnetwork.com/recipes/food-network-kitchen/chicken-fettuccine-alfredo-3364118"
        },
        {
            "title": "Chicken Biryani",
            "image": "https://image.freepik.com/free-photo/indian-chicken-biryani-served-terracotta-bowl-with-yogurt-white-background-selective-focus_466689-72554.jpg",
            "link": "https://www.recipetineats.com/biryani/"
        }
    ]



def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

@app.route('/')
def home():
   fetch_data = '''SELECT * FROM recipes''' 
   available_recipes = execute_read_query(conn, fetch_data)
   
   return render_template("home.html", recipes=available_recipes)

@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/recipe/', methods=['POST', 'GET'])
def create_recipe():
    form = CreateRecipeForm() #instantiate the form to send when the request.method != POST
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        if form.validate():
            title = form.title.data #access the form data
            image = form.image.data
            link = form.link.data
            insert_recipe = '''INSERT INTO recipes (title, image, link) VALUES (?,?,?)'''
            data = (title, image, link)
            execute_query(conn, insert_recipe, data)
            return redirect(url_for('home'))
    return render_template('create-recipe.html', form=form) # return the form to the template

@app.route('/recipe/delete/<id>/', methods=['POST'])
def delete_recipe(id):
    execute_query(conn, '''DELETE FROM recipes WHERE id=?''', (id))
    return redirect(url_for("home"))
   

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def show_recipe(id):
    form = CreateRecipeForm()
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        if form.validate():
            title = form.title.data
            image = form.image.data
            link = form.link.data
            update_query = f'''UPDATE recipes set title=?, image=?, link=? WHERE id = {id}'''
            execute_query(conn, update_query, (title, image, link))
            return redirect(url_for('home'))
    select_query = f'''SELECT * FROM recipes WHERE id={id}'''
    recipe = execute_read_query(conn, select_query)
    form = CreateRecipeForm(link=recipe[0][3], title=recipe[0][1], image=recipe[0][2])
    return render_template('edit-recipe.html', form=form, id=id)

if __name__ == '__main__':
    

    conn = create_connection("recipes.db")
    execute_query(conn, create_recipes_table)
    app.run(debug=True)
    

