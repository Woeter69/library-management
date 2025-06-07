import mysql.connector
from tabulate import tabulate
from datetime import *
from colorama import *
mydb=mysql.connector.connect(host="localhost",user="root",passwd="stillalive")
cur=mydb.cursor()
cur.execute("create database if not exists Library")
cur.execute("use library")


def create_categories_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            Category_ID INT PRIMARY KEY,
            Category_Name VARCHAR(255) NOT NULL
        )
    """)


def create_books_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            Book_ID INT PRIMARY KEY,
            Title VARCHAR(255) NOT NULL,
            Author VARCHAR(255) NOT NULL,
            Category_ID INT,
            Quantity INT NOT NULL,
            FOREIGN KEY (Category_ID) REFERENCES Categories(Category_ID)
        )
    """)  


def create_members_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Members (
            User_ID VARCHAR(50) PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Phone VARCHAR(50),
            Address VARCHAR(255),
            Password VARCHAR(255) NOT NULL,
            Active_Status BOOLEAN DEFAULT TRUE
        )
    """)
    

def create_loans_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Loans (
            Loan_ID INT PRIMARY KEY AUTO_INCREMENT,
            Member_ID VARCHAR(40),
            Book_ID INT,
            Loan_Date DATE,
            Return_Date DATE,
            FOREIGN KEY (Member_ID) REFERENCES Members(User_ID),
            FOREIGN KEY (Book_ID) REFERENCES Books(Book_ID) ON DELETE CASCADE
        )
    """)
    

def create_fines_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Fines (
            Fine_ID INT PRIMARY KEY AUTO_INCREMENT,
            Member_ID Varchar(40),
            Amount DECIMAL(10, 2),
            Due_Date DATE,
            FOREIGN KEY (Member_ID) REFERENCES Members(User_ID)
        )
    """)
    

create_categories_table()
create_books_table()
create_members_table()
create_loans_table()
create_fines_table()


def admin_add_book():
    while True:
        book_id = input("Enter Book ID: ")
        title = input("Enter Book Title: ")
        author = input("Enter Book Author: ")
        category_id = input("Enter Category ID: ")
        quantity = input("Enter Quantity: ")

        cur.execute("INSERT INTO Books (Book_ID, Title, Author, Category_ID, Quantity) VALUES(%s, %s, %s, %s, %s)",(book_id, title, author, category_id, quantity))
        mydb.commit()
        print(Fore.GREEN+"Book added successfully!")
        print(Style.RESET_ALL)


        add_more = input("Do you want to add another book? (Y/N): ")
        if add_more == 'n' or add_more=='N':
            break


def admin_view_books():
    cur.execute("SELECT * FROM Books")
    books = cur.fetchall()
    print(Back.YELLOW+"Books in the Library:")
    print(Style.RESET_ALL)
    print(tabulate(books, headers=["Book ID", "Title", "Author", "Category ID", "Quantity"],tablefmt=mysql))


def admin_delete_book():
    book_id = input("Enter Book ID to delete: ")
    cur.execute("DELETE FROM Books WHERE Book_ID = %s", (book_id,))
    mydb.commit()
    print(Fore.RED+"Book deleted successfully!")
    print(Style.RESET_ALL)


def admin_update_book():
    book_id = input("Enter Book ID to update: ")
    field = input("Which field do you want to update? Title/Author/Category ID/Quantity ")
    value = input(f"Enter new value for {field}: ")
    cur.execute(f"UPDATE Books SET {field.capitalize()} = %s WHERE Book_ID = %s", (value, book_id))
    mydb.commit()
    print(Fore.YELLOW+"Book updated successfully!")
    print(Style.RESET_ALL)


def admin_view_members():
    cur.execute("SELECT * FROM Members")
    members = cur.fetchall()
    print(Back.YELLOW+"Members in the Library:")
    print(Style.RESET_ALL)
    print(tabulate(members, headers=["Member ID", "Name", "Phone", "Address", "Password","Active Status"],tablefmt=mysql))


def admin_update_fine():
    member_id = input("Enter Member ID to update fine: ")
    amount = input("Enter Fine Amount: ")
    due_date = input("Enter Due Date (YYYY-MM-DD): ")
    description = input("Enter reason for the fine (e.g., Damaged book, Lost book): ")
    cur.execute("INSERT INTO Fines (Member_ID, Amount, Due_Date, Description) VALUES (%s, %s, %s, %s)",(member_id, amount, due_date, description))
    mydb.commit()
    print(Fore.YELLOW+"Fine updated successfully!")
    print(Style.RESET_ALL)


def admin_cancel_membership():
    m=input('Enter Member Id to cancel their Membership ')
    cur.execute("UPDATE Members SET Active_Status = FALSE WHERE User_ID = %s", (m,))

    print(Fore.RED+f"Membership of {m} is Cancelled by Admins")


def admin_reactive_membership():
    m=input('Enter Member Id to Reactivate their Membership ')
    cur.execute("UPDATE Members SET Active_Status = TRUE WHERE User_ID = %s", (m,))
    cur.execute("DELETE FROM FINES WHERE MEMBER_ID=%s",(m,))

    print(Fore.GREEN+f"Membership of {m} is Reactivated and All Fines are Deleted by Admins")


def cancel_membership_if_due():
    today = datetime.now().date()
    cutoff_date = today - timedelta(days=30)
    
    cur.execute("SELECT DISTINCT Member_ID FROM Fines WHERE Due_Date < %s", (cutoff_date,))
    members_due = cur.fetchall()
    
    for (member_id,) in members_due:
        cur.execute("UPDATE Members SET Active_Status = FALSE WHERE ACTIVE_STATUS = TRUE AND User_ID  = %s", (member_id,))
        

def admin_view_loans():
    cur.execute("SELECT * FROM Loans")
    loans = cur.fetchall()
    print(Back.YELLOW+"Current Loans:")
    print(Style.RESET_ALL)
    print(tabulate(loans, headers=["Loan ID", "Member ID", "Book ID", "Loan Date", "Return Date"]))


def admin_return_loan():
    cur.execute("SELECT * FROM Loans")
    loans = cur.fetchall()
    if not loans:
        print(Fore.RED+"No Loans Available")
    else:
        print(Back.YELLOW+"Available Loans:")
        print(Style.RESET_ALL)
        print(tabulate(loans, headers=["Loan ID", "Member ID", "Book ID", "Loan Date", "Return Date"]))

    
        loan_id = input("Enter Loan ID to return: ")
    
        return_date = datetime.now().date()
        cur.execute("UPDATE Loans SET Return_Date = %s WHERE Loan_ID = %s", (return_date, loan_id))
        mydb.commit()

        cur.execute("SELECT Book_ID FROM Loans WHERE Loan_ID = %s", (loan_id,))
        book_id = cur.fetchone()[0]
        cur.execute("UPDATE Books SET Quantity = Quantity + 1 WHERE Book_ID = %s", (book_id,))
        cur.execute("DELETE FROM Loans WHERE LOAN_ID = %s",(loan_id,))
        mydb.commit()

        print(Fore.GREEN+"Loan returned successfully!")
        print(Style.RESET_ALL)



def admin_update_fines_daily():
    today = datetime.now().date()
    cur.execute("SELECT Member_ID, Book_ID, Loan_Date FROM Loans WHERE Return_Date IS NULL")
    active_loans = cur.fetchall()

    for member_id, book_id, return_date in active_loans:
        days_overdue = (today - (return_date)).days
        if days_overdue > 0:  
            fine_amount = days_overdue * 3  # Rs 3 per day
            due_date = today  
            
            
            cur.execute("SELECT * FROM Fines WHERE Member_ID = %s AND Book_ID = %s", (member_id, book_id))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO Fines (Member_ID, Book_ID, Amount, Due_Date) VALUES (%s, %s, %s, %s)",(member_id, book_id, fine_amount, due_date))
            else:
                cur.execute("UPDATE Fines SET Amount = Amount + %s, Due_Date = %s WHERE Member_ID = %s AND Book_ID = %s",(fine_amount, due_date, member_id, book_id))

            print(Fore.YELLOW+f"Fine updated for Member ID {member_id}, Book ID {book_id}. Total fine: Rs {fine_amount}")
            print(Style.RESET_ALL)

    mydb.commit()


def user_register():
    while True:
        user_id = input("Enter User ID to be Registered: ")
        cur.execute("SELECT * FROM Members WHERE User_ID = %s", (user_id,))
        if cur.fetchone():
            print(Fore.RED+"User ID already exists. Please try a different User ID.")
            continue
        
        name = input("Enter Name: ")
        phone = input("Enter Phone Number: ")
        address = input("Enter Address: ")
        password = input("Enter Password: ")

        cur.execute("INSERT INTO Members (User_ID, Name, Phone, Address, Password) VALUES(%s, %s, %s, %s, %s)",(user_id, name, phone, address, password))
        mydb.commit()
        print(Fore.GREEN+"Registration successful! You are now a member.")
        break


def user_view_books():
    cur.execute("SELECT * FROM Books")
    books = cur.fetchall()
    print(Back.YELLOW+"Available Books:")
    print(Style.RESET_ALL)
    print(tabulate(books, headers=["Book ID", "Title", "Author", "Category ID", "Quantity"],tablefmt=mysql))


def user_view_details():
    member_id=input("Enter User_ID: ")
    cur.execute(f"select User_ID, Name, Phone, Address, Active_Status from members where User_ID=%s",(member_id,))
    members=cur.fetchall()
    print(Back.YELLOW+"Your User details are: ")
    print(Style.RESET_ALL)
    print(tabulate(members,headers=["User_ID","Name","Phone","Address","Active_Status"],tablefmt=mysql))


def order_book():
    member_id = input("Enter your Member ID: ")
    password = input("Enter your Password: ")

    cur.execute("SELECT Active_Status FROM Members WHERE User_ID = %s", (member_id,))
    ans=cur.fetchone()

    if ans is None:
        print(Fore.RED+"User not found.")
        return
    
    status=ans[0]

    if not status:
        print(Fore.RED+"You are a inactive member.You Cannot Order Books.")
        print(Style.RESET_ALL)
        return


    cur.execute("SELECT Password FROM Members WHERE User_ID = %s", (member_id,))
    result = cur.fetchone()

    if result is None:
        print(Fore.RED+"Member ID not found.")
        print(Style.RESET_ALL)
        return

    if result[0] != password:
        print(Fore.RED+"Incorrect password.")
        print(Style.RESET_ALL)
        return

    book_id = input("Enter the Book ID you want to borrow: ")

    cur.execute("SELECT Quantity FROM Books WHERE Book_ID = %s", (book_id,))
    result = cur.fetchone()

    if result is None or result[0] <= 0:
        print(Fore.RED+"Sorry, this book is not available.")
        print(Style.RESET_ALL)
        return

    loan_date = datetime.now().date()
    return_date = loan_date + timedelta(days=7)  

    cur.execute("INSERT INTO Loans (Member_ID, Book_ID, Loan_Date, Return_Date) VALUES (%s, %s, %s, %s)",(member_id, book_id, loan_date, return_date))
    mydb.commit()

    cur.execute("UPDATE Books SET Quantity = Quantity - 1 WHERE Book_ID = %s", (book_id,))
    mydb.commit()

    print(Fore.GREEN+f"Book ID {book_id} has been successfully borrowed by Member ID {member_id} on {loan_date}.")
    print(Style.RESET_ALL)
    print(Fore.YELLOW+f"Please return the book by {return_date}.")
    print(Style.RESET_ALL)


def main():
    while True:
        print(Fore.CYAN+"1: Admin Panel")
        print(Fore.CYAN+"2: User Panel")
        print(Fore.CYAN+"3: Exit")
        print(Style.RESET_ALL)
        choice = input("Choose an option: ")

        if choice == '1':
            admin_password = input("Enter Admin Password: ")
            if admin_password == "admin":  
                while True:
                    print(Fore.CYAN+"Admin Options:")
                    print(Style.RESET_ALL)
                    print(Fore.BLUE+"1: Add Book")
                    print(Fore.BLUE+"2: View Books")
                    print(Fore.BLUE+"3: Update Book")
                    print(Fore.BLUE+"4: Delete Book")
                    print(Fore.BLUE+"5: View Members")
                    print(Fore.BLUE+"6: Update Fines")
                    print(Fore.BLUE+"7: Cancel Memberships")
                    print(Fore.BLUE+"8: Reactivate Memberships")
                    print(Fore.BLUE+"9: View Loans")
                    print(Fore.BLUE+"10: Return Loan")
                    print(Fore.BLUE+"11: Exit Admin Panel")
                    print(Style.RESET_ALL)
                    admin_choice = input("Choose an option: ")

                    if admin_choice == '1':
                        admin_add_book()
                    elif admin_choice == '2':
                        admin_view_books()
                    elif admin_choice == '3':
                        admin_update_book()
                    elif admin_choice == '4':
                        admin_delete_book()
                    elif admin_choice == '5':
                        admin_view_members()
                    elif admin_choice == '6':
                        admin_update_fine()
                    elif admin_choice == '7':
                        admin_cancel_membership()
                    elif admin_choice=='8':
                        admin_reactive_membership()
                    elif admin_choice == '9':
                        admin_view_loans()
                    elif admin_choice == '10':
                        admin_return_loan()
                    elif admin_choice == '11':
                        break
                    else:
                        print(Fore.RED+"Invalid choice, please try again.")
                        print(Style.RESET_ALL)
            else:
                print(Fore.RED+"Incorrect password!")
                print(Style.RESET_ALL)

          
        elif choice=='2':
            print("1:Registration")
            print("2:User Details")
            print("3:Order Books")

            ch=input("Choose an option: ")
            if ch=='1':
                user_register()
            elif ch=='2':
                user_view_details()
            elif ch=='3':
                user_view_books()
                order_book()
        elif choice == '3':
            print(Fore.RED+"Exiting the system.")
            print(Style.RESET_ALL)
            break
        else:
            print(Fore.RED+"Invalid choice, please try again.")
            print(Style.RESET_ALL)
            
admin_update_fines_daily()
cancel_membership_if_due()
main()



