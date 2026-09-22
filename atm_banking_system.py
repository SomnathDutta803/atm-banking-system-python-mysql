
import pymysql

# Connect to MySQL database
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Abcd1234",
    database="ATMMachine1",
    port=3310
)

cursor = conn.cursor()

print("MySQL Connected Successfully!")


def get_amount(message):
    try:
        amount = int(input(message))
        if amount <= 0:
            print("Amount must be greater than 0!")
            return None
        return amount
    except ValueError:
        print("Please enter a valid number!")
        return None


def account_exists(acc):
    cursor.execute(
        "SELECT ACCONT_NO FROM ATMMoney WHERE ACCONT_NO=%s",
        (acc,)
    )
    return cursor.fetchone() is not None


def get_balance(acc):
    cursor.execute(
        "SELECT BALANCE FROM ATMMoney WHERE ACCONT_NO=%s",
        (acc,)
    )
    result = cursor.fetchone()
    return result[0] if result else 0


try:
    while True:

        print("\nWELCOME TO OUR ATM MONEY TRANSACTION")
        print("-" * 50)
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")

        try:
            ch = int(input("Enter your choice: "))
        except ValueError:
            print("Please enter a valid choice!")
            continue

        # CREATE ACCOUNT
        if ch == 1:

            acc = input("Enter an 8-digit account number: ")

            if len(acc) != 8 or not acc.isdigit():
                print("Account number must contain exactly 8 digits!")
                continue

            if account_exists(acc):
                print("Account number already exists!")
                continue

            name = input("Enter your name: ").strip()

            if not name:
                print("Name cannot be empty!")
                continue

            pwd = input("Enter your 6-digit PIN: ")

            if len(pwd) != 6 or not pwd.isdigit():
                print("Invalid PIN! Enter exactly 6 digits.")
                continue

            deposit = get_amount(
                "Enter initial deposit (minimum 1000): "
            )

            if deposit is None:
                continue

            if deposit < 1000:
                print("Minimum initial deposit is 1000!")
                continue

            try:
                cursor.execute(
                    """INSERT INTO ATMMoney
                    (ACCONT_NO, PASSWORD, NAME, CR_AMT, WITHDRAWL, BALANCE)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (acc, pwd, name, deposit, 0, deposit)
                )

                conn.commit()

                print("Account created successfully!")
                print("Your account number:", acc)
                print("Your balance:", deposit)

            except pymysql.MySQLError as e:
                conn.rollback()
                print("Account creation failed:", e)

        # LOGIN
        elif ch == 2:

            acc = input("Enter account number: ")
            pwd = input("Enter 6-digit PIN: ")

            cursor.execute(
                """SELECT ACCONT_NO, NAME
                FROM ATMMoney
                WHERE ACCONT_NO=%s AND PASSWORD=%s""",
                (acc, pwd)
            )

            user = cursor.fetchone()

            if not user:
                print("Invalid account number or PIN!")
                continue

            print("Login Successful!")
            print("Welcome", user[1])

            # ATM MENU
            while True:

                print("\n1. Deposit")
                print("2. Withdraw")
                print("3. Transfer Money")
                print("4. Check Balance")
                print("5. Change Account Number")
                print("6. Logout")

                try:
                    opt = int(input("Enter your choice: "))
                except ValueError:
                    print("Please enter a valid choice!")
                    continue

                # DEPOSIT
                if opt == 1:

                    amt = get_amount("Enter amount to deposit: ")

                    if amt is None:
                        continue

                    if amt > 300000:
                        print("Maximum deposit is 300000!")
                        continue

                    cursor.execute(
                        """UPDATE ATMMoney
                        SET CR_AMT = CR_AMT + %s,
                            BALANCE = BALANCE + %s
                        WHERE ACCONT_NO = %s""",
                        (amt, amt, acc)
                    )

                    conn.commit()
                    print("Amount deposited successfully!")

                # WITHDRAW
                elif opt == 2:

                    amt = get_amount("Enter amount to withdraw: ")

                    if amt is None:
                        continue

                    if amt > 50000:
                        print("Maximum withdrawal is 50000!")
                        continue

                    bal = get_balance(acc)

                    if amt > bal:
                        print("Insufficient balance!")
                    else:
                        cursor.execute(
                            """UPDATE ATMMoney
                            SET WITHDRAWL = WITHDRAWL + %s,
                                BALANCE = BALANCE - %s
                            WHERE ACCONT_NO = %s""",
                            (amt, amt, acc)
                        )

                        conn.commit()
                        print("Amount withdrawn successfully!")

                # TRANSFER MONEY
                elif opt == 3:

                    acc1 = input(
                        "Enter receiver's 8-digit account number: "
                    )

                    if len(acc1) != 8 or not acc1.isdigit():
                        print("Invalid account number!")
                        continue

                    if acc1 == acc:
                        print("Cannot transfer to your own account!")
                        continue

                    if not account_exists(acc1):
                        print("Receiver account does not exist!")
                        continue

                    amt = get_amount("Enter amount to transfer: ")

                    if amt is None:
                        continue

                    bal = get_balance(acc)

                    if amt > bal:
                        print("Insufficient balance!")
                        continue

                    try:
                        # Deduct from sender
                        cursor.execute(
                            """UPDATE ATMMoney
                            SET WITHDRAWL = WITHDRAWL + %s,
                                BALANCE = BALANCE - %s
                            WHERE ACCONT_NO = %s""",
                            (amt, amt, acc)
                        )

                        # Add to receiver
                        cursor.execute(
                            """UPDATE ATMMoney
                            SET CR_AMT = CR_AMT + %s,
                                BALANCE = BALANCE + %s
                            WHERE ACCONT_NO = %s""",
                            (amt, amt, acc1)
                        )

                        conn.commit()
                        print("Money transferred successfully!")

                    except pymysql.MySQLError as e:
                        conn.rollback()
                        print("Transfer failed:", e)

                # CHECK BALANCE
                elif opt == 4:

                    bal = get_balance(acc)
                    print("Current Balance:", bal)

                # CHANGE ACCOUNT NUMBER
                elif opt == 5:

                    acc2 = input("Enter your new 8-digit account number: ")

                    if len(acc2) != 8 or not acc2.isdigit():
                        print("Please enter exactly 8 digits!")
                        continue

                    if account_exists(acc2):
                        print("This account number already exists!")
                        continue

                    try:
                        cursor.execute(
                            """UPDATE ATMMoney
                            SET ACCONT_NO = %s
                            WHERE ACCONT_NO = %s""",
                            (acc2, acc)
                        )

                        conn.commit()

                        acc = acc2

                        print("Account number changed successfully!")
                        print("Your new account number:", acc)

                    except pymysql.MySQLError as e:
                        conn.rollback()
                        print("Account number change failed:", e)

                # LOGOUT
                elif opt == 6:

                    print("Logged out successfully!")
                    break

                else:
                    print("Invalid choice!")

        # EXIT
        elif ch == 3:
            print("Thank you! Visit again.")
            break

        else:
            print("Invalid choice!")

finally:
    cursor.close()
    conn.close()
    print("Database connection closed.")
