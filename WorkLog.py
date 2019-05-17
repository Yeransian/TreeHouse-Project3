import csv
import sys
import os
import datetime
import re

welcome = '\n***Welcome to Work Log for Python Command Line***\n'


def work_log():
    '''stores information about tasks including name, time spent, and optional
    notes.  Tasks can be searched, edited, and deleted.
    '''
    menu = """\nSelect from the following options:\n
      1 - Enter new task
      2 - Search for existing task
      3 - Quit\n
    """
    print(menu)
    menu_select = None
    while not menu_select:
        menu_select = input('>>>')
        if menu_select == '1':
            task_entry()
        elif menu_select == '2':
            task_search()
        elif menu_select == '3':
            sys.exit(0)
        elif menu_select.lower() == 'm':
            print(menu)
            menu_select = None
        else:
            print("Please select an option from 1, 2, 3, m=menu")
            menu_select = None


def task_entry():
    '''Allows user to enter a task name, time spent, and optional notes'''
    # define name, time, notes, and date variables
    name = time = notes = date = None
    # get input for each of these
    while not name or name.isspace():
        name = input('Enter a name for the task or q to quit.\n>>>')
        if name.lower() == 'q':
            sys.exit(0)
    while not time:
        try:
            time = int(input('Enter time spent on task in minutes.\n>>>'))
        except ValueError:
            print("Please enter a valid number")
    notes = input("Enter any notes about the task (optional).\n>>>")
    if notes.isspace():
        notes = None
    date = datetime.datetime.now().strftime('%m/%d/%Y')
    # insert input into file
    with open('worklog.csv', 'a+', newline='') as taskfile:
        fieldnames = ['name', 'time', 'notes', 'date']
        writer = csv.DictWriter(taskfile, fieldnames=fieldnames)
        # if file is newly created, write headers first
        if os.stat('worklog.csv').st_size == 0:
            writer.writeheader()
        # write input information as row
        writer.writerow({'name': name, 'time': time,
                         'notes': notes, 'date': date})
    repeat = input("The task was added.  Enter another task? [Y/n]")
    if repeat.lower() == 'y':
        task_entry()
    else:
        work_log()


def task_search():
    '''Allows user to search, edit, and delete task entries from file'''
    menu = '''\nSelect from the following options:\n
        1 - Find by date
        2 - Find by time spent
        3 - Find by exact search
        4 - Find by regular expression
        5 - Return to main menu\n
    '''
    print(menu)
    search_mode = None
    while not search_mode:
        search_mode = input('>>>').strip()
        if search_mode == '1':
            date_find()
        elif search_mode == '2':
            time_find()
        elif search_mode == '3':
            exact_find()
        elif search_mode == '4':
            regex_find()
        elif search_mode == '5':
            work_log()
        else:
            print("Please enter a selection from 1 to 5")
            search_mode = None


def date_input(date_wrapper):
    '''Asks for date and validates for format MM/DD/YYYY'''
    # Function takes lists rather than strings since strings are immutable
    while len(date_wrapper) == 0:
        try:
            input_string = input('>>>')
            date_wrapper.append(datetime.datetime.strptime(
                                input_string, '%m/%d/%Y'))
        except ValueError:
            print('Date must be valid and in format MM/DD/YYYY. Try again.')


def date_find():
    '''Searches for all entries matching a specific date
    or falling within a date range.
    '''
    # Dates are lists so that they can be passed into date_input and modified
    search_date_1 = []
    search_date_2 = []
    search_mode = None
    while not search_mode:
        search_mode = input('Enter 1 to search specific date '
                            'or 2 to search within a date range.\n>>>').strip()
        if search_mode not in ['1', '2']:
            print('Not a valid selection')
            search_mode = None
    print('Input {}date in format MM/DD/YYYY'.format(
          'start ' if search_mode == '2' else ''))
    date_input(search_date_1)
    if search_mode == '2':
        print('Input end date in format MM/DD/YYYY')
        while not search_date_2:
            date_input(search_date_2)
            # make sure search_date1 is no later than search_date2
            if search_date_1[0].timestamp() > search_date_2[0].timestamp():
                print('First date cannot be later than second date. '
                      'Enter end date again.')
                search_date_2 = []
    # run search
    search_results = []
    with open('worklog.csv') as taskfile:
        reader = csv.DictReader(taskfile)
        if search_mode == '1':
            for row in reader:
                if (datetime.datetime.strptime(row['date'], '%m/%d/%Y') ==
                        search_date_1[0]):
                    search_results.append(row)
        else:
            for row in reader:
                if ((datetime.datetime.strptime(
                        row['date'], '%m/%d/%Y').timestamp() >=
                        search_date_1[0].timestamp()) and
                    (datetime.datetime.strptime(
                        row['date'], '%m/%d/%Y').timestamp() <=
                        search_date_2[0].timestamp())):
                    search_results.append(row)
    if len(search_results) == 0:
        print('\nNo results found.\n')
        task_search()
    else:
        display_results(search_results)


def time_find():
    search_time = None
    search_results = []
    print("Enter task time to the nearest minute")
    while search_time is None:
        search_time = input('>>>')
        try:
            search_time = int(search_time)
        except ValueError:
            print("Enter a valid number")
            search_time = None
        else:
            search_time = str(search_time)
    with open('worklog.csv') as taskfile:
        reader = csv.DictReader(taskfile)
        for row in reader:
            if row['time'] == search_time:
                search_results.append(row)
    if len(search_results) == 0:
        print('\nNo results found.\n')
        task_search()
    else:
        display_results(search_results)


def exact_find():
    search_string = None
    search_results = []
    print('Enter text to be searched')
    while search_string is None or search_string.isspace():
        search_string = input('>>>')
        if search_string.strip() == '':
            print("Please enter some text to be searched.")
            search_string = None
    with open('worklog.csv') as taskfile:
        reader = csv.DictReader(taskfile)
        for row in reader:
            if (row['name'].find(search_string) > -1 or
                    row['notes'].find(search_string) > -1):
                search_results.append(row)
    if len(search_results) == 0:
        print('\nNo results found.\n')
        task_search()
    else:
        display_results(search_results)


def regex_find():
    search_exp = None
    search_results = []
    print("Enter a valid regular expression.")
    while search_exp is None:
        search_exp = input('>>>')
        try:
            search_exp = re.compile(search_exp)
        except re.error:
            print("That is not a valid regular expression. Try again.")
            search_exp = None
    with open('worklog.csv') as taskfile:
        reader = csv.DictReader(taskfile)
        for row in reader:
            if (re.search(search_exp, row['name']) or
                re.search(search_exp, row['time']) or
                re.search(search_exp, row['notes']) or
                    re.search(search_exp, row['date'])):
                search_results.append(row)
    if len(search_results) == 0:
        print('\nNo results found.\n')
        task_search()
    else:
        display_results(search_results)


def display_results(results_list):
    '''Displays search results one by one,
allowing each entry to be edited or deleted.'''
    count = 1
    for entry in results_list:
        print('''
            Result {} of {}\n
            Task name: {}
            Work time: {}
            Date: {}
            Notes: {}
'''.format(count, len(results_list), entry['name'],
              entry['time'], entry['date'], entry['notes']))
        selection = None
        while not selection:
            selection = input('Select {}[E]dit entry, '
                              '[D]elete entry, [S]earch menu \n>>>'
                              .format('[N]ext result, ' if count <
                                      len(results_list) else ''))
            if selection.lower() == 'e':
                edit_entry(entry)
            elif selection.lower() == 'd':
                delete_entry(entry)
            elif selection.lower() == 's':
                # go back to search menu
                return task_search()
            elif selection.lower() != 'n':
                selection = None
        count += 1
    print("\nEnd of search results.\n")
    task_search()


def edit_entry(task_dict):
    '''Allows user to edit specific field of task entry'''
    field_dict = {'1': 'name', '2': 'time', '3': 'date', '4': 'notes'}
    field = None
    while not field:
        field = input('''Select field to edit: 1 - name, 2 - time, 3 - date, 4 - notes.
Enter 5 to go back to search results, 6 to go back to search menu\n>>>''')
        if field == '5':
            return
        if field == '6':
            return task_search()
    print('The {} of the current entry is {}'.format(
          field_dict[field], task_dict[field_dict[field]]))
    new_info = None
    while not new_info:
        new_info = input('Enter new {}\n>>>>'.format(field_dict[field]))
        if new_info.isspace():
            new_info = None
            continue
        if field == '2':
            try:
                new_info = int(new_info)
            except ValueError:
                print("Please enter a valid number")
                new_info = None
            else:
                new_info = str(new_info)
        if field == '3':
            try:
                datetime.datetime.strptime(new_info, '%m/%d/%Y')
            except ValueError:
                print("Dates should be valid and in format mm/dd/YYYY")
                new_info = None
    edited = []
    with open('worklog.csv') as taskfile:
        reader = csv.DictReader(taskfile)
        for row in reader:
            if row == task_dict:
                row[field_dict[field]] = new_info
                edited.append(row)
            else:
                edited.append(row)
    with open('worklog.csv', 'w', newline='') as taskfile:
        fieldnames = ['name', 'time', 'notes', 'date']
        writer = csv.DictWriter(taskfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in edited:
            writer.writerow({'name': row['name'], 'time': row['time'],
                            'notes': row['notes'], 'date': row['date']})
    print("\nEntry edited!\n")


def delete_entry(task_dict):
    '''Allows user to delete task entry'''
    edited = []
    with open('worklog.csv') as taskfile:
        reader = csv.DictReader(taskfile)
        for row in reader:
            if row == task_dict:
                continue
            else:
                edited.append(row)
    with open('worklog.csv', 'w', newline='') as taskfile:
        fieldnames = ['name', 'time', 'notes', 'date']
        writer = csv.DictWriter(taskfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in edited:
            writer.writerow({'name': row['name'], 'time': row['time'],
                            'notes': row['notes'], 'date': row['date']})
    print("\nEntry deleted!\n")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":

    work_log()
