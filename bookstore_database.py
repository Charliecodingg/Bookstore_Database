'''This program provides functionality for a clerk at a bookstore to store data on books.
They can add new books to the database, update books information, delete books from the database
or search the database to find a book. The database is automatically populated with some default
book stock.
'''
#====Module Section====#
import sqlite3

#This imports the tabulate module, but if the import fails sets the variable to true.
no_table = False
try:
    from tabulate import tabulate
except:
    no_table = True


#====Database Setup====#

db = sqlite3.connect('ebookstore')
cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS
    books(id INTEGER PRIMARY KEY,Title TEXT UNIQUE NOT NULL, Author TEXT NOT NULL,
    Qty INTEGER NOT NULL)
''')
db.commit()

#this creates a table with four columns and commits it to the database
default_books = [(3001,'A Tale of Two Cities','Charles Dickens',30),
(3002,'Harry Potter and the Philosopher\'s Stone','J.K. Rowling',40),
(3003,'The Lion, the Witch and the Wardrobe','C.S. Lewis',25),
(3004,'The Lord of the Rings','J.R.R. Tolkien',37),
(3005,'Alice in Wonderland','Lewis Carroll',12),
(3006,'American Gods','Neil Gaiman',45),
(3007,'Goodnight Punpun','Inio Asano',13),
(3008,'Mordew','Alex Pheby',65),
(3009,'Consider Philebas','Iain M. Banks',25),
(3010,'House of Leaves','Mark Z. Danielewski',3),
(3011,'The Eye of the World','Robert Jordan',53),
(3012,'The Pillars of the Earth','Ken Follett',2)]

#Here are our default values to insert into the table, only if the table is empty
cursor.execute('''
SELECT COUNT(*) FROM books
''')
count = cursor.fetchone()

if count[0] == 0:
    cursor.executemany('''
        INSERT INTO books(id, Title, Author, Qty) VALUES(?,?,?,?)''',default_books)
    db.commit()
#If the table is empty then the default values are inserted, otherwise they are ignored
#for these default values id is assigned, new entries will be auto incrimented

#====Function Section====#
def view_books():
    #This function selects every row and displays them for the user
    cursor.execute('''
    SELECT * FROM books
    ''')
    if no_table == True:
        for row in cursor:
            print('ID : {0} Title : {1}. Author : {2}. Quantity : {3}'.format(row[0],row[1],row[2],row[3]))
    else:
        book_table(cursor)
        #if the user has the tabluate module this calls a function with the current cursor

def book_table(cursor):
    '''this function creates an empty list, then appends the nested data from each object
    in the cursor to it. This data is used with headers named after the columns to display
    the data in a easy to read grid'''
    book_table = []
    for book in cursor:
        book_table.append([book[0],book[1],book[2],book[3]])
        #this loop creates a nested list with all the book data
    head = ["ID","Title","Author","Quantity"]
    #the header plus the new list are used to build the table 
    print(tabulate(book_table,headers=head,tablefmt="grid"))
    

def add_book():
    while True:
        new_title = input("Please enter the title for the new book or -1 to abandon book entry: ")
        #This ensures the Title of the new book is not null as required by the database
        if len(new_title) > 0 and new_title != '-1':
            break
        else:
            print("Please enter the Title of the book or -1 to abandon book entry: ")
        if new_title.strip() == '-1':
            return
    if book_check(new_title) == False:
        return
        #this uses a simple case sensitive check for duplicate titles, returning user to menu if found
    while True:
        new_author = input("Please enter the author of this book or -1 to abandon book entry: ")
        #This ensures the Author of the book is not null
        if len(new_author) > 0 and new_author != '-1':
            break
        else:
            #This allows the user to return to the main menu if they wish before completing the entry
            print("Please enter the Authors name or -1 to abandon book entry: ")
        if new_author.strip() == '-1':
            return
    while True:
        try:
            #this ensures the quantity of the book is not null and allows the user to return to menu
            new_qty = input("Please enter the stock for this book or -1 to abandon book entry: ")
            new_qty = int(new_qty)
            if new_qty == -1:
                return
            if new_qty < 0:
                print("Please enter a positive number: ")
            else:
                break
            #This avoids errors with stock being set to negative values, the loop exits after check
        except:
            print("Please only enter a numerical value or -1 to abandon book entry: ")
    new_book = (new_title, new_author, new_qty)
    #With the inputs checked and assigned to the new_book tuple they are inserted
    cursor.execute('''
    INSERT INTO books(Title,Author,Qty)
    VALUES(?,?,?)
    ''', new_book)
    db.commit()
    #the new book is now in the database with its auto-increment Id as its primary key
def update_book_find():
    '''This function allows the user to select a book already present in the list
    then passes the result book to a new function which updates an aspect of the book
    that they select. They can find the book using several inputs not only id number'''
    if no_table == True:
        print('''
        1: ID
        2: Title
        3: Author
        ''')
    else:
        option_table = [['1:', ' Title'],['2:',' Author'],['3:',' Quantity']]
        print(tabulate(option_table,tablefmt="grid"))
    #This logic ensures the option is an integer between 0 and 4. If it is -1 then function is ended
    while True:
        update_find_option = input("Please select how you would like to search for the book to update or -1 to return to main menu: ")
        try:
            update_find_option = int(update_find_option)
            if update_find_option == -1:
                return
            if update_find_option > 0 and update_find_option < 4:
                break
            else:
                print("Please select an option from the menu or -1 to return to the main menu: ")
        except:
            print("Please select an option from the menu or -1 to return to the main menu: ")
    #====Search Section====#
    if update_find_option == 1:
        #For updating by ID we need to verify the users input is the correct format
        id_found = False
        #The id found variable allows the user to continue searching via ids
        #if their previous entry is valid but not found.
        while id_found == False:
            while True:
                update_id = input("Please enter the four digit id of the book or -1 to return to the main menu: ")
                try:
                    update_id = int(update_id)
                    if update_id == -1:
                        return
                    if len(str(update_id)) == 4: 
                        break
                        #The loop continues until an integer four digits long is entered or -1 is used
                    else:
                        print("Please ensure the id is four digits long")
                except:
                    print("Please enter a number")
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE id = ?) 
            ''', (update_id,))
            #this checks if an entry into the database with matching id exists
            found = cursor.fetchone()
            #because IDs are unique fetchone is used
            if found[0] == 0:
                print("ID not found")
            else:
                #This exits the loop and enters the update phase
                id_found = True
                cursor.execute('''
                SELECT * FROM books WHERE id = ? 
                ''', (update_id,))
                result = cursor.fetchone()
                #the information about the selected book is collected into a variable
                
    elif update_find_option == 2:
        title_found = False
        #This loop continues until a matching title is entered or -1 is used to exit to main menu
        while title_found == False:
            update_title = input("Please enter the title of the book you are updating, this is case-sensitive or -1 to return to the main menu: ")
            if update_title.strip() == '-1':
                return
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE Title = ?) 
            ''', (update_title,))
            found = cursor.fetchone()
            if found[0] == 0:
                print("Title not found")
            else:
                title_found = True
                cursor.execute('''
                SELECT * FROM books WHERE Title = ? 
                ''', (update_title,))
                result = cursor.fetchone()
                #The record found is used to pass into the update book change function
    elif update_find_option == 3:
        author_found = False
        #this loop continues until a matching author is found or -1 is used to exit
        while author_found == False:
            update_author = input("Please enter the Author of the book you are updating, this is case-sensitive or -1 to return to the main menu: ")
            if update_author.strip() == '-1':
                return
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE Author = ?) 
            ''', (update_author,))
            found = cursor.fetchone()
            if found[0] == 0:
                print("Author not found")
            else:
                #Once an author is found things become more complicated
                author_found = True
        results = list()
        #an empty list of results is made to store all books by the found author
        cursor.execute('''
        SELECT * FROM books WHERE Author = ? 
        ''', (update_author,))
        for row in cursor:
            author_result = list()
            #for each row or book on the cursor a list in the list of results is appended
            for value in row:
                author_result.append(value)
                #Because we are using the search results in the second function all values that might be chosen are needed
            results.append(author_result)
            #after the whole cursor is looped through a selection menu is built
        if len(results) == 1:
            result = results[0]
            #if the author only has one book then that book is auto-selected
        else:
            x = 1
            #if the author has multiple books then the user needs to select the one to update
            if no_table == True:
                for option in results:
                    print(f"Enter {x} to select ID:{option[0]} , {option[1]}, {option[2]}, {option[3]} as the book to update")
                    x += 1
                    #using x as an iterant integer beside the option variable allows us to use it to select
            else:
                #if the user has the tabulate module then the results are built into a grid.
                    book_table = []
                    for option in results:
                        book_table.append([x,option[0],option[1],option[2],option[3]])
                        x += 1
                        #this loop creates a nested list with all the book data
                    head = ["Select","ID","Title","Author","Quantity"]
                    #the header plus the new list are used to build the table 
                    print(tabulate(book_table,headers=head,tablefmt="grid"))
                    print("Enter the selection number to select a book: ")
                    #functionality wise the table and non table options have the same method of use
            while True:
                author_selection = input("")
                try: 
                    author_selection = int(author_selection)
                    if author_selection <= len(results) and author_selection > 0:
                        author_selection += -1
                        #it is given minus one to match it up with the index value of the displayed option
                        result = results[author_selection]
                        #the final result is the list that matches this selection
                        break
                    else:
                        print("Please enter a valid number, or -1 to return to main menu: ")
                except:
                    print("Please enter a number to select an author's book")
    #The record found is used to pass into the update book change function
    update_book_change(result)

def update_book_change(search_result):
    #this function uses the results of the search to allow a user to update the book in a way they desire
    print(f"Select what aspect of {search_result[1]} you would like to update or -1 to return to the main menu: ")
    if no_table == True:
        print('''
        1: Title
        2: Author
        3: Quantity
        ''')
    else:
        option_table = [['1:', ' Title'],['2:',' Author'],['3:',' Quantity']]
        print(tabulate(option_table,tablefmt="grid"))
    while True:
        #This ensures the input is an acceptable integer
        update_change_option = input("")
        try:
            update_change_option = int(update_change_option)
            if update_change_option == -1:
                return
            if update_change_option > 0 and update_change_option < 4:
                break
            else:
                print("Please select an option from the menu or -1 to return to the main menu: ")
        except:
            print("Please select an option from the menu or -1 to return to the main menu: ")
    if update_change_option == 1:
        print(f"The current Title is: {search_result[1]}")
        
        #The new title is checked for duplication to reduce errors
        while True:
            new_title = input("Please enter the new title for the book or -1 to return to the main menu: ")
            if book_check(new_title) != False:
                break
            if new_title.strip() == '-1':
                return
        #With the final check completed the database is finally updated
        cursor.execute('''
        UPDATE books SET Title = ? WHERE id = ?
        ''',(new_title,search_result[0]))
        #The id from the search results is used to find the correct record to update
        db.commit()
    elif update_change_option ==2:
        print(f"The current Author is: {search_result[2]}")
        new_author = input("Please enter the new author or -1 to return to the main menu: ")
        if new_author.strip() == '-1':
            return
        #Because there can be multiple books by the same author there are less checks needed
        cursor.execute('''
        UPDATE books SET Author = ? WHERE id = ?
        ''',(new_author,search_result[0]))
        #The id from the search results is used to find the correct record to update
        db.commit()
    elif update_change_option == 3:
        print(f"The current Quantity is: {search_result[3]}")
        while True:
            new_qty = input("Please enter the new quantity of the book or -1 to return to main menu: ")
            try:
                new_qty = int(new_qty)
                if new_qty == -1:
                    return
                if new_qty > 0: 
                    break
                    #The loop continues until the new quantity is positive or -1 is used
                else:
                        print("Please ensure the new quantity is positive")
            except:
                    print("Please only enter a number")
        #With the quantity checked it can now be commited to the database
        cursor.execute('''
        UPDATE books SET Qty = ? WHERE id = ?
        ''',(new_qty,search_result[0]))
        #The id from the search results is used to find the correct record to update
        db.commit()
def delete_book():
    #This function allows the user to select a record to delete using the unique ID.
    cursor.execute('''
    SELECT * FROM books
    ''')
    ID_list = list()
    for row in cursor:
        if no_table == True:
            print('ID : {0} Title : {1}. Author : {2}. Quantity : {3}'.format(row[0],row[1],row[2],row[3]))
            #This displays the information about each book for the user if there is no tabulate.
        ID_list.append(row[0])
        #This loop displays the books for the user and also builds a list of valid IDs dynamically
    if no_table == False:
        #the cursor needs to be reset after ID list is build to be gone through again
        cursor.execute('''
        SELECT * FROM books
        ''')
        book_table(cursor)
        #If there is a tabulate module then the grid is displayed after the id list is built.
    while True:
        deletion_selection = input("Enter the ID of the book you wish to delete or -1 to return to main menu: ")
        try:
            deletion_selection = int(deletion_selection)
            #The input is checked to be an integer and in the list of valid IDs
            if deletion_selection == -1:
                return
            if deletion_selection in ID_list:
                cursor.execute('''
                DELETE FROM books WHERE id = ?
                ''',(deletion_selection,))
                db.commit()
                #The deletion is confirmed and a message is displayed for confirmation
                print("Book successfully deleted")
                break
            else:
                print("Please enter a valid ID")
        except:
            print("Please enter a number")
def search_books():
    #This function allows the user to search through the database to display records matching their selection
    if no_table == True:
        print('''
        1: ID
        2: Title
        3: Author
        4: Quantity
        ''')
    else:
        option_table = [['1:', ' ID'],['2:','Title'],['3:',' Author'],['4:',' Quantity']]
        print(tabulate(option_table,tablefmt="grid"))
    #This logic ensures the option is an integer between 0 and 5. If it is -1 then function is ended
    while True:
        search_option = input("Please select how you would like to search for the book or -1 to return to main menu: ")
        try:
            search_option = int(search_option)
            if search_option == -1:
                return
            if search_option > 0 and search_option < 5:
                break
            else:
                print("Please select an option from the menu: ")
        except:
            print("Please select an option from the menu: ")
    #With the selection ensured to be valid now the search can begin
    if search_option == 1:
        id_found = False
        #This loop continues until a matching ID is entered or -1 is used to exit to main menu
        while id_found == False:
            search_id = input("Please enter the ID of the book or -1 to return to the main menu: ")
            try:
                search_id = int(search_id)
                if search_id == -1:
                    return
            except:
                print("Please enter a number")
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE id = ?) 
            ''', (search_id,))
            found = cursor.fetchone()
            if found[0] == 0:
                print("ID not found")
            else:
                #Once a matching ID is found the whole record of that book is displayed to the user
                id_found = True
                cursor.execute('''
                SELECT * FROM books WHERE id = ? 
                ''', (search_id,))
                if no_table == True:
                    for row in cursor:
                        print(f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}, Quantity: {row[3]}")
                else:
                    book_table(cursor)
                    #if the user has the tablulate module it will build a small grid to display

    elif search_option == 2:
        title_found = False
        #This loop continues until a matching title is entered or -1 is used to exit to main menu
        while title_found == False:
            search_title = input("Please enter the title of the book, this is case-sensitive or -1 to return to the main menu: ")
            if search_title.strip() == '-1':
                return
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE Title = ?) 
            ''', (search_title,))
            found = cursor.fetchone()
            if found[0] == 0:
                print("Title not found")
            else:
                #Once a matching title is found the whole record of that title is displayed to the user
                title_found = True
                cursor.execute('''
                SELECT * FROM books WHERE Title = ? 
                ''', (search_title,))
                if no_table == True:
                    for row in cursor:
                        print(f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}, Quantity: {row[3]}")
                else:
                    book_table(cursor)
                    #if the user has the tabulate module the record is displayed in a small grid
                
    elif search_option == 3:
        author_found = False
        while author_found == False:
            search_author = input("Enter the Author you would like to search for, this is case-sensitive or -1 to return to the main menu: ")
            if search_author.strip() == '-1':
                return
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE Author = ?) 
            ''', (search_author,))
            found = cursor.fetchone()
            if found[0] == 0:
                print("Author not found")
            else:
                author_found = True
        cursor.execute('''
        SELECT * FROM books WHERE Author = ?
        ''',(search_author,))
        if no_table == True:
            for row in cursor:
                print(f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}, Quantity: {row[3]}")
            #this prints each matching result for the user,as this can return multiple records
        else:
            book_table(cursor)
            #This will display a grid of each of an authors works if the user has the tabulate module

    elif search_option == 4:
        qty_found = False
        while qty_found == False:
            while True:
                #This loop checks that the input is an integer before conducting a search
                search_qty = input("Enter the Quantity you would like to search for or -1 to return to main menu: ")
                try:
                    search_qty = int(search_qty)
                    break
                except:
                    print("Please enter a number only")
            if search_qty == -1:
                return
            cursor.execute('''
            SELECT EXISTS (SELECT * FROM books WHERE Qty = ?) 
            ''', (search_qty,))
            found = cursor.fetchone()
            if found[0] == 0:
                print("Quantity not found")
            else:
                qty_found = True
            cursor.execute('''
            SELECT * FROM books WHERE qty = ?
            ''',(search_qty,))
            if no_table == True:
                for row in cursor:
                    print(f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}, Quantity: {row[3]}")
                    #this prints each matching result for the user,as this can return multiple records
            else:
                book_table(cursor)
                #or if they have the tabulate module a grid of each book with that quantity will be built

def book_check(book_title):
    #This function is called from the add book function to check that a 
    #case-sensitive book titles will help reduce duplicate entries
    cursor.execute('''
    SELECT * FROM books
    WHERE Title = ?
    ''', (book_title,))
    results = cursor.fetchall()
    if results != []:
        #if a result is found, meaning a match happened the user cannot add a new entry for this book
        print("This book is already in the database, Please use the update book option from the menu to add additional stock")
        return False

#====Menu Section====#
menu_choice = 0
#The menu loops until -1 is entered which breaks the loop and closes the program
while menu_choice != -1:
    if no_table == True:
        print('''
        1: View current books
        2: Add new book
        3: Update book information
        4: Delete book
        5: Search for book
        Or -1 to exit the program''')
        print("Please select the function you would like to perform:")
    else:
        menu_table = [['1:', ' View current books'],
        ['2:',' Add new book'],
        ['3:',' Update book information'],
        ['4:',' Delete book'],
        ['5:',' Search for book'],
        ['-1:',' Exit the program']]
        menu_header = ["","Option"]
        print(tabulate(menu_table,headers=menu_header,tablefmt="grid"))
        print("Please select the function you would like to perform:")
    while True:
        menu_choice = input("")
        try:
            menu_choice = int(menu_choice)
            break
        except:
            print("Please enter a number from the menu")
    if menu_choice == 1:
        #calls the view books function
        view_books()
    elif menu_choice == 2:
        #calls the add book function
        add_book()
    elif menu_choice == 3:
        #calls the update book function
        update_book_find()
    elif menu_choice == 4:
        #calls the delete book function
        delete_book()
    elif menu_choice == 5:
        #calls the search book function
        search_books()

print("Thank you for using the Bookstore database ")
#Closes the database connection
db.close()