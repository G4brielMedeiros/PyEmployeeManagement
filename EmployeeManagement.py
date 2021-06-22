
# GABRIEL LINS MEDEIROS

# This application manages a simple list of employees, storing their name and salary.

import sqlite3

# Employee class to be used internally.


class Employee:
    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay


# SQL statements collected for the database connection.
SQL_stats = []

# Items brought to memory from the database.
# This list represents the database before it is saved.
employee_list = []

# SQL insert/delete/update statements to be formatted in functions.
# Created to make the program easier to code.
SQL_insert = "INSERT INTO employees VALUES (:first, :last, :pay)"
SQL_delete = "DELETE FROM employees WHERE first = :first AND last = :last AND pay = :pay"
SQL_update_pay = "UPDATE employees SET pay = :new_pay " \
                 "WHERE first = :first AND last = :last AND pay = :pay"
SQL_update_name = "UPDATE employees SET first = :new_first, last = :new_last " \
                  "WHERE first = :first AND last = :last AND pay = :pay"


# Asks the user for a name and a salary, then generates an employee object for employee_list.
# This function also generates the SQL statement for the SQL_stats list.


def insert():
    prompt = input('firstname lastname pay     '
                   '( Example: John Smith 5000 )\n').strip().title().split(' ')
    try:
        employee_list.append(Employee(prompt[0], prompt[1], int(prompt[2])))
        SQL_stats.append((SQL_insert, {'first': prompt[0], 'last': prompt[1], 'pay': int(prompt[2])}))
    except ValueError:
        print('ValueError. Try again.')


# Deletes the employee object from employee_list in the position passed as an argument.
# IT also generates the SQL statement for the SQL_stats list.
# Made to be used in the select function for readability.


def delete(sel):
    choice = input('Are you sure? Type YES, otherwise press Enter.\n').upper()
    emp = employee_list[sel]
    if choice == 'YES':
        print(emp.first, emp.last, 'is gone.')
        SQL_stats.append([SQL_delete, {'first': emp.first, 'last': emp.last, 'pay': emp.pay}])
        del employee_list[sel]
    else:
        print(emp.first, emp.last, 'was not removed.')


# Asks the user to edit either the name or salary of an employee from employee_list
# in the position passed as an argument. This also creates the corresponding
# SQL statement for the SQL_stats list.


def edit(sel):
    print('1 - New name')
    print('2 - New salary')
    choice = input()
    if choice == '1':
        first_name = input('Enter new first name:').capitalize()
        last_name = input('Enter new last name:').capitalize()
        if first_name.isspace() or first_name == '' or last_name.isspace() or last_name == '':
            print('Error: Name must not be empty.')
        else:
            SQL_stats.append((SQL_update_name,
                              {'first': employee_list[sel].first,
                               'last': employee_list[sel].last,
                               'pay': employee_list[sel].pay,
                               'new_first': first_name,
                               'new_last': last_name}))
            employee_list[sel].first = first_name
            employee_list[sel].last = last_name
            print('Employee renamed to', employee_list[sel].first, employee_list[sel].last, '.')

    elif choice == '2':
        new_pay = int(input('Enter new salary: '))

        SQL_stats.append((SQL_update_pay,
                          {'first': employee_list[sel].first,
                           'last': employee_list[sel].last,
                           'pay': employee_list[sel].pay,
                           'new_pay': new_pay}))
        employee_list[sel].pay = new_pay
        print('Salary changed to $', employee_list[sel].pay, '.')


# Lists everyone in employee_list, then prompts the user to select a person or cancel.
# This will determine if the user would like to edit or remove an employee,
# and call the appropriate function.


def select():
    detail = "{0} {1}:      ${2}"
    place = 0
    print('Select person to edit/remove. 0 to cancel.')
    for item in employee_list:
        place += 1
        print(place, '-', detail.format(item.first, item.last, item.pay))

    try:
        sel = int(input()) - 1

        choice = -1
        if 0 <= sel <= place:
            print('You selected:', employee_list[sel].first, employee_list[sel].last)
            print('1 - Edit person')
            print('2 - Remove person')
            choice = input()
        else:
            pass

    #   EDIT
        if choice == '1':
            edit(sel)

    #   DELETE
        elif choice == '2':
            delete(sel)
    except ValueError:
        pass
    except IndexError:
        print("IndexError: Position not found.")

# Confirms the user intention, then either does nothing,
# or clears employee_list and sends a DELETE SQL statement to SQL_statements.


def delete_everything():
    choice = input('Are you sure? This will remove EVERYONE. Type YES, otherwise press Enter.\n').upper()
    if choice == 'YES':
        print('All your items are gone.')
        employee_list.clear()
        SQL_stats.append(("DELETE FROM employees", {}))
    else:
        print('Your employees were not removed.')


# Main function. Console user interface, that determines what the user wants to do with the list,
# calling the appropriate function for each action.


def management(database):
    for item in database:
        employee_list.append(Employee(item[0], item[1], item[2]))
    while True:
        print('\n')
        print('ITEM MANAGER')
        print('1 - List everyone')
        print('2 - Insert new employee')
        print('3 - Delete everyone')
        print('0 - Exit')

        selection = input('')

#       LIST DETAILS
        if selection == '1':
            if len(employee_list) > 0:
                select()
            else:
                print("The list is empty.")


#       INSERT SQL
        elif selection == '2':
            try:
                insert()
            except TypeError:
                print('TypeError. Try again.')
            except IndexError:
                print('IndexError. Try again.')


#       DELETE EVERYTHING SQL
        elif selection == '3':
            delete_everything()


#       EXIT SQL
        elif selection == '0':
            leave = input('Save your changes? YES/NO/CANCEL\n').upper()
            if leave == 'YES':
                return SQL_stats
            elif leave == 'NO':
                break
            else:
                continue


# # # ##### SQLITE SECTION BELOW ##### # # #

# Connects to the database.
conn = sqlite3.connect('Employees.db')

# Instantiates a cursor.
c = conn.cursor()

# Creates a table if not already there.
c.execute("""CREATE TABLE IF NOT EXISTS employees (
                first text,
                last text,
                pay integer
        )""")

# Selects all from items table.
c.execute("SELECT * FROM employees")

# Initiates the program by calling Management() and passing all items from database as argument.
# When management() is done, it returns everything from SQL_stats.
statements = management(c.fetchall())

# Loops through all SQL statements (if any) and executes them in order, after program closes.
if statements:
    for stat in statements:
        print(stat)
        c.execute(stat[0], stat[1])
        conn.commit()

# Close connection with the database.
conn.close()
