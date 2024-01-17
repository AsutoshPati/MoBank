"""
    Project Name:       Mo Bank (A dummy banking system)
    Author:             Asutosh Pati (https://in.linkedin.com/in/asutoshpati)
    Date of Creation:   13 Jul. 2019
    Purpose:            For training purpose
    Description:
        "Mo Bank" is a hands-on educational project designed to teach Python programming through the development of a 
        simulated banking system. Leveraging the PyQt module, the app features an intuitive graphical interface that 
        replicates essential banking operations, including money deposit, withdrawal, fund transfers, and account 
        statement generation. Users can assume different roles such as Customer, Bank Staff, and Administrator, gaining 
        insights into diverse user experiences. The project incorporates database management for secure user data 
        storage and retrieval, along with file handling techniques for logging and data storage tasks. "Mo Bank" 
        provides students with a practical and interactive learning environment, reinforcing Python skills, GUI 
        development, database management, and file handling concepts. It is a valuable tool for those seeking a 
        comprehensive understanding of Python's applications in the context of a banking system.

        ADVISORY:
            This program, authored by Asutosh Pati, is intended solely for educational purposes. Unauthorized use of 
            this project without the author's explicit consent is strictly prohibited. The program is permitted for 
            teaching purposes only, subject to the author's approval, and any other utilization of this software is 
            strictly prohibited.

    Version:
        V 0.0.1: Released with beta version
        V 1.0.0: Enhanced new UI, Different tabs for different role
        V 1.1.0: Add transaction view
        V 2.0.0: New UI, Single window experience, pdf report generation
"""

################################   Libraries   ################################
import ctypes
from datetime import datetime
from dateutil.relativedelta import relativedelta
from functools import partial
import hashlib
import math
import os
import re
import secrets
import sqlite3 as sql
import sys
import tempfile
import webbrowser

from fpdf import FPDF

from PyQt5 import uic, QtCore
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)


# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    # try:
    #     # PyInstaller creates a temp folder and stores path in _MEIPASS
    #     base_path = sys._MEIPASS
    # except Exception:
    #     base_path = os.path.abspath(".")
    base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


#############################   Global variables   ############################
DB_PATH = resource_path("assets\\mo_bank.db")

main_win = None
user_details = dict()
last_login_time = None


##############################   Load UI pages   ##############################
class Intro(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\intro.ui"), self)


class Login(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\login.ui"), self)


class AccountDetails(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\acc_details.ui"), self)


class HolderWithdrawl(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\holder_withdrawl.ui"), self)


class CustomerTransactions(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\holder_trans.ui"), self)


class SWO_Deposit(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\swo_deposit.ui"), self)


class SWO_Withdrawl(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\swo_withdrawl.ui"), self)


class SWO_Transfer_Money(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\swo_transfer_money.ui"), self)


class SWO_Transactions(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\swo_trans.ui"), self)


class AdminCreateUser(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\admin_new_user.ui"), self)


class AdminUpdateUser(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\admin_update_user.ui"), self)


class AdminTransactions(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\admin_trans.ui"), self)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(resource_path("assets\\pages\\main_win.ui"), self)

        # Page 0
        self.intro = Intro()
        self.stackedWidget.addWidget(self.intro)

        # Page 1
        self.login = Login()
        self.stackedWidget.addWidget(self.login)

        # Page 2
        self.acc_det = AccountDetails()
        self.stackedWidget.addWidget(self.acc_det)

        # Page 3
        self.hldr_wdrl = HolderWithdrawl()
        self.stackedWidget.addWidget(self.hldr_wdrl)

        # Page 4
        self.customer_trans = CustomerTransactions()
        self.stackedWidget.addWidget(self.customer_trans)

        # Page 5
        self.swo_dep = SWO_Deposit()
        self.stackedWidget.addWidget(self.swo_dep)

        # Page 6
        self.swo_wdrl = SWO_Withdrawl()
        self.stackedWidget.addWidget(self.swo_wdrl)

        # Page 7
        self.swo_tf_mn = SWO_Transfer_Money()
        self.stackedWidget.addWidget(self.swo_tf_mn)

        # Page 8
        self.swo_trans = SWO_Transactions()
        self.stackedWidget.addWidget(self.swo_trans)

        # Page 9
        self.admin_new_user = AdminCreateUser()
        self.stackedWidget.addWidget(self.admin_new_user)

        # Page 10
        self.admin_update = AdminUpdateUser()
        self.stackedWidget.addWidget(self.admin_update)

        # Page 11
        self.admin_trans = AdminTransactions()
        self.stackedWidget.addWidget(self.admin_trans)


################################   Create PDF   ################################
class PDF(FPDF):
    # Page header
    def header(self):
        # Logo
        self.image(
            resource_path("assets\\images\\Mo Bank logo.JPG"), x=60, y=10, w=20, h=20
        )
        self.set_font("helvetica", style="B", size=32)
        self.cell(80)
        self.cell(
            30, 20, self.title, border=0, new_x="LMARGIN", new_y="NEXT", align="C"
        )
        self.ln(10)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font("helvetica", style="I", size=8)
        # Page number
        self.cell(
            0,
            10,
            "Page " + str(self.page_no()) + "/{nb}",
            border=0,
            new_x="LMARGIN",
            new_y="NEXT",
            align="R",
        )


#############################   Helper functions   ############################
def encrypt_password(pwd: str) -> str:
    return hashlib.md5(pwd.encode()).hexdigest()


def generate_password() -> str:
    return secrets.token_urlsafe(nbytes=8)


def initial_db_check():
    print(DB_PATH)
    # Check or Create Database
    conn = sql.Connection(DB_PATH)
    conn.close()

    # Create tables if doesn't exist
    conn = sql.Connection(DB_PATH)
    try:
        query = "SELECT * FROM AccountDetails LIMIT 1;"
        conn.execute(query)
    except sql.OperationalError:
        query = """CREATE TABLE IF NOT EXISTS AccountDetails( 
        acc_no INTEGER PRIMARY KEY AUTOINCREMENT, 
        acc_type TEXT DEFAULT "C", 
        full_name TEXT NOT NULL, 
        email TEXT NOT NULL UNIQUE, 
        mobile TEXT NOT NULL UNIQUE, 
        gender TEXT DEFAULT "O", 
        dob TEXT, 
        password TEXT NOT NULL, 
        user_type TEXT NOT NULL DEFAULT "Holder", 
        curr_bal NUMERIC NOT NULL);"""
        conn.execute(query)
        query = """INSERT INTO AccountDetails VALUES(100001, "C", "Admin", "admin@mobank.xy", "9999999999", "M", 
        "2024-01-01", "e20f517179e9cd52ae29dae43c121b95", "A", 100000.0);"""  # password - Hello@123
        conn.execute(query)
        conn.commit()
        print("Table AccountDetails created")
    conn.close()

    conn = sql.Connection(DB_PATH)
    try:
        query = "SELECT * FROM Transactions LIMIT 1;"
        conn.execute(query)
    except sql.OperationalError:
        query = """CREATE TABLE IF NOT EXISTS Transactions(
        txn_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        acc_no INTEGER, 
        timestamp TEXT NOT NULL, 
        operation TEXT NOT NULL, 
        prev_bal NUMERIC NOT NULL, 
        trans_amount NUMERIC NOT NULL, 
        avail_bal NUMERIC NOT NULL, 
        operation_details TEXT, 
        operator INTEGER, 
        CONSTRAINT fk_acc FOREIGN KEY (acc_no) REFERENCES AccountDetails(acc_no),
        CONSTRAINT fk_operator FOREIGN KEY (operator) REFERENCES AccountDetails(acc_no));"""
        conn.execute(query)
        query = """INSERT INTO Transactions VALUES(30000001, 100001, "2024-01-01 12:57:01.564427", "Cr", 0.0, 100000.0, 
        100000.0, "Account opening balance", 100001);"""
        conn.execute(query)
        conn.commit()
        print("Table Transactions created")
    conn.close()


def validate_fullname(name: str) -> tuple:
    # add your name validation logic here
    if len(name) < 2:
        return False, "Full name should have atleast 2 characters"
    return True, ""


def validate_email(email: str) -> bool:
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    return True if re.fullmatch(regex, email) else False


def validate_mobile(mobile: str) -> bool:
    regex = r"\b^\+?[6-9][0-9]{9}$\b"
    return True if re.fullmatch(regex, mobile) else False


def validate_password(pwd: str) -> tuple:
    # add your password validation logic here
    if len(pwd) < 6:
        return False, "Password should have atleast 6 characters"
    return True, ""


def validate_account_no(acc_no: str) -> bool:
    ret = False
    if len(acc_no) >= 6:
        try:
            int(acc_no)
            ret = True
        except ValueError:
            pass
    return ret


def generate_report(
    user_data, trans_data, from_date: str, to_date: str, is_emp: bool = False
):
    pdf = PDF()
    pdf.title = "Mo Bank"
    pdf.set_margins(left=12.7, top=12.7)
    pdf.alias_nb_pages()
    pdf.add_page()

    TABLE_CELL_HEIGHT = 6

    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(40, 10, "Account Details")
    pdf.ln(15)

    pdf.set_font(style="", size=12)
    pdf.cell(
        pdf.epw / 2,
        TABLE_CELL_HEIGHT,
        f"**Account Number:** {user_data[0]}",
        border=1,
        align="L",
        markdown=True,
    )
    print_msg = ""
    if not is_emp:
        print_msg = (
            f"**Account Type:** {'Current' if user_data[1] == 'C' else 'Savings'}"
        )
    pdf.cell(
        pdf.epw / 2, TABLE_CELL_HEIGHT, print_msg, border=1, align="L", markdown=True
    )
    pdf.ln(TABLE_CELL_HEIGHT)
    pdf.cell(
        pdf.epw,
        TABLE_CELL_HEIGHT,
        f"**Account Holder:** {user_data[2]}",
        border=1,
        align="L",
        markdown=True,
    )
    pdf.ln(TABLE_CELL_HEIGHT)
    if not is_emp:
        pdf.cell(
            pdf.epw / 2,
            TABLE_CELL_HEIGHT,
            f"**Email:** {user_data[3]}",
            border=1,
            align="L",
            markdown=True,
        )
        pdf.cell(
            pdf.epw / 2,
            TABLE_CELL_HEIGHT,
            f"**Mobile:** +91{user_data[4]}",
            border=1,
            align="L",
            markdown=True,
        )
        pdf.ln(TABLE_CELL_HEIGHT)
        pdf.cell(
            pdf.epw / 2,
            TABLE_CELL_HEIGHT,
            f"**DoB:** {user_data[6]}",
            border=1,
            align="L",
            markdown=True,
        )
        pdf.cell(pdf.epw / 2, TABLE_CELL_HEIGHT, "", border=1, align="L", markdown=True)
        pdf.ln(TABLE_CELL_HEIGHT)
        pdf.cell(pdf.epw / 2, TABLE_CELL_HEIGHT, "", border=1, align="L", markdown=True)
        pdf.cell(
            pdf.epw / 2,
            TABLE_CELL_HEIGHT,
            f"**Available Balance:** {user_data[9]:.2f}",
            border=1,
            align="L",
            markdown=True,
        )
    pdf.ln(20)

    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(40, 10, "Account Statement")
    pdf.ln(15)

    pdf.set_font(style="", size=12)
    pdf.cell(
        pdf.epw / 2,
        TABLE_CELL_HEIGHT,
        f"**From Date:** {from_date}",
        border=1,
        align="L",
        markdown=True,
    )
    pdf.cell(
        pdf.epw / 2,
        TABLE_CELL_HEIGHT,
        f"**To Date:** {to_date}",
        border=1,
        align="L",
        markdown=True,
    )
    pdf.ln(TABLE_CELL_HEIGHT)

    pdf.cell(25, TABLE_CELL_HEIGHT, "**Date**", border=1, align="L", markdown=True)
    pdf.cell(
        69.60, TABLE_CELL_HEIGHT, "**Details**", border=1, align="L", markdown=True
    )
    pdf.cell(30, TABLE_CELL_HEIGHT, "**Amount**", border=1, align="L", markdown=True)
    pdf.cell(30, TABLE_CELL_HEIGHT, "**Operation**", border=1, align="L", markdown=True)
    pdf.cell(30, TABLE_CELL_HEIGHT, "**Balance**", border=1, align="L", markdown=True)
    pdf.ln(TABLE_CELL_HEIGHT)

    pdf.set_font(size=11)
    cr_val = 0
    db_val = 0
    for row in trans_data:
        lines = math.ceil(pdf.get_string_width(row[7]) / 69.60)
        row_height = TABLE_CELL_HEIGHT * lines
        pdf.cell(25, row_height, row[2][:10], border=1, align="L")
        pdf.cell(69.60, row_height, row[7], border=1, align="L")
        pdf.cell(30, row_height, f"{row[5]:.2f}", border=1, align="L")
        pdf.cell(30, row_height, row[3], border=1, align="L")
        pdf.cell(30, row_height, f"{row[6]:.2f}", border=1, align="L")
        pdf.ln(row_height)

        if row[3] == "Cr":
            cr_val += row[5]
        elif row[3] == "Db":
            db_val += row[5]

    if is_emp:
        pdf.ln(TABLE_CELL_HEIGHT)
        pdf.cell(
            pdf.epw / 2,
            TABLE_CELL_HEIGHT,
            f"**Total Transaction:** {cr_val + db_val:.2f}",
            border=1,
            align="L",
            markdown=True,
        )
        pdf.cell(
            pdf.epw / 2,
            TABLE_CELL_HEIGHT,
            f"**Floating Amount:** {cr_val - db_val:.2f}",
            border=1,
            align="L",
            markdown=True,
        )
        pdf.ln(TABLE_CELL_HEIGHT)

    # Create a temporary PDF file
    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(temp_file_path)

    # Open the temporary PDF file in the default system PDF viewer
    webbrowser.open(temp_file_path, new=2)


########################   Function to open UI pages   ########################
def show_message_box(msg_type: str = "info", msg: str = ""):
    """
    Show a message popup box with the information like success or error messages

    Parameters
    ----------
    msg_type : str, optional
        Type of message to be displayed (info|error). The default is "info".
    msg : str, optional
        Message to be displayed in the message box. The default is "".

    Returns
    -------
    None.

    """
    msg_box = QMessageBox()
    msg_box.setWindowTitle("PMS")
    msg_box.setWindowIcon(QIcon(resource_path("assets\\images\\Mo Bank logo.jpg")))
    if msg_type == "error":
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("OOPS!!")
    else:
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Information")
    msg_box.setInformativeText(msg)
    msg_box.setStandardButtons(QMessageBox.Close)
    msg_box.exec_()


def openIntroPage():
    main_win.stackedWidget.setCurrentIndex(0)


def openLoginPage():
    # Clear the input fields
    main_win.login.lineEdit.setText("")
    main_win.login.lineEdit_2.setText("")

    main_win.stackedWidget.setCurrentIndex(1)


def openAccountDetailsPage():
    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {user_details["acc_no"]} LIMIT 1"""
    ret = conn.execute(query)
    data = ret.fetchone()
    conn.close()

    main_win.acc_det.label_24.setText(str(user_details["acc_no"]))
    main_win.acc_det.label_17.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.acc_det.label_18.setText(data[3])
    main_win.acc_det.label_19.setText(data[4])

    gender = None
    if data[5] == "M":
        gender = "Male"
    elif data[5] == "F":
        gender = "Female"
    elif data[5] == "O":
        gender = "Other"
    main_win.acc_det.label_20.setText(gender)

    main_win.acc_det.label_21.setText(
        datetime.strptime(data[6], "%Y-%m-%d").strftime("%d-%m-%Y")
    )

    acc_type = None
    if data[1] == "C":
        acc_type = "Current"
    elif data[1] == "S":
        acc_type = "Savings"
    main_win.acc_det.label_22.setText(acc_type)

    main_win.acc_det.label_23.setText(f"₹{data[9]:.2f}")

    main_win.acc_det.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.acc_det.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(2)


def openCustomerWithdrawlPage():
    main_win.hldr_wdrl.label_9.setText("Enter Amount to Withdrawl")

    main_win.hldr_wdrl.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.hldr_wdrl.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(3)


def openCustomerTransPage():
    main_win.customer_trans.dateEdit.setDate(datetime.now() - relativedelta(months=1))
    main_win.customer_trans.dateEdit_2.setDate(datetime.now())
    main_win.customer_trans.tableWidget.setRowCount(0)

    main_win.customer_trans.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.customer_trans.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(4)


def openSWO_DepositPage():
    if user_details["role"] == "C":
        show_message_box(
            msg_type="error", msg="Only Admins and SWO can access this page"
        )
        return

    main_win.swo_dep.lineEdit.setText("")
    main_win.swo_dep.label_10.setText("")
    main_win.swo_dep.label_11.setText("")
    main_win.swo_dep.label_14.setText("")
    main_win.swo_dep.spinBox.setValue(10)

    main_win.swo_dep.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.swo_dep.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(5)


def openSWO_WithdrawlPage():
    if user_details["role"] == "C":
        show_message_box(
            msg_type="error", msg="Only Admins and SWO can access this page"
        )
        return

    main_win.swo_wdrl.lineEdit.setText("")
    main_win.swo_wdrl.label_10.setText("")
    main_win.swo_wdrl.label_11.setText("")
    main_win.swo_wdrl.label_14.setText("")
    main_win.swo_wdrl.spinBox.setValue(10)

    main_win.swo_wdrl.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.swo_wdrl.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(6)


def openSWO_TransferPage():
    if user_details["role"] == "C":
        show_message_box(
            msg_type="error", msg="Only Admins and SWO can access this page"
        )
        return

    main_win.swo_tf_mn.lineEdit.setText("")
    main_win.swo_tf_mn.lineEdit_2.setText("")
    main_win.swo_tf_mn.label_10.setText("")
    main_win.swo_tf_mn.label_11.setText("")
    main_win.swo_tf_mn.label_14.setText("")
    main_win.swo_tf_mn.label_16.setText("")
    main_win.swo_tf_mn.spinBox.setValue(10)

    main_win.swo_tf_mn.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.swo_tf_mn.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(7)


def openSWO_TransPage():
    if user_details["role"] == "C":
        show_message_box(
            msg_type="error", msg="Only Admins and SWO can access this page"
        )
        return

    main_win.swo_trans.lineEdit.setText("")
    main_win.swo_trans.dateEdit.setDate(datetime.now() - relativedelta(months=1))
    main_win.swo_trans.dateEdit_2.setDate(datetime.now())
    main_win.swo_trans.label_12.setText("")
    main_win.swo_trans.tableWidget.setRowCount(0)

    main_win.swo_trans.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.swo_trans.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(8)


def openNewCustomerPage():
    if user_details["role"] != "A":
        show_message_box(msg_type="error", msg="Only Admins can access this page")
        return

    # Clear the input fields
    main_win.admin_new_user.lineEdit.setText("")
    main_win.admin_new_user.lineEdit_2.setText("")
    main_win.admin_new_user.lineEdit_3.setText("")
    main_win.admin_new_user.lineEdit_4.setText(generate_password())
    main_win.admin_new_user.comboBox.setCurrentIndex(0)
    main_win.admin_new_user.comboBox_2.setCurrentIndex(0)
    main_win.admin_new_user.dateEdit.setDate(datetime.now() - relativedelta(years=18))
    main_win.admin_new_user.spinBox.setValue(100)

    main_win.admin_new_user.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.admin_new_user.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(9)


def openKYC_Page(clear_acc_no: bool = True):
    if user_details["role"] != "A":
        show_message_box(msg_type="error", msg="Only Admins can access this page")
        return

    # Clear the input fields
    if clear_acc_no:
        main_win.admin_update.lineEdit.setText("")
    main_win.admin_update.lineEdit_2.setText("")
    main_win.admin_update.lineEdit_3.setText("")
    main_win.admin_update.lineEdit_4.setText("")
    main_win.admin_update.lineEdit_5.setText("")
    main_win.admin_update.comboBox.setCurrentIndex(0)
    main_win.admin_update.comboBox_2.setCurrentIndex(0)
    main_win.admin_update.comboBox_3.setCurrentIndex(0)
    main_win.admin_update.dateEdit.setDate(datetime.now() - relativedelta(years=18))

    main_win.admin_update.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.admin_update.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(10)


def openTransactionPage():
    if user_details["role"] != "A":
        show_message_box(msg_type="error", msg="Only Admins can access this page")
        return

    # Clear the input fields
    main_win.admin_trans.lineEdit.setText("")
    main_win.admin_trans.label_12.setText("")
    main_win.admin_trans.dateEdit.setDate(datetime.now() - relativedelta(months=1))
    main_win.admin_trans.dateEdit_2.setDate(datetime.now())
    main_win.admin_trans.tableWidget.setRowCount(0)

    main_win.admin_trans.label_5.setText(
        user_details["prefix"] + " " + user_details["name"]
    )
    main_win.admin_trans.label_6.setText("Loggedin At: " + last_login_time)

    main_win.stackedWidget.setCurrentIndex(11)


########################   Functions used in UI pages   #######################
def openGithubRepo():
    url = "https://github.com/AsutoshPati/MoBank"
    webbrowser.open(url, new=0, autoraise=True)


def openGithubProfile():
    url = "https://github.com/AsutoshPati"
    webbrowser.open(url, new=0, autoraise=True)


def completeLogin():
    global user_details, last_login_time

    user_info = main_win.login.lineEdit.text()
    password = main_win.login.lineEdit_2.text()
    password = encrypt_password(password)

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE (email = "{user_info}" OR mobile = "{user_info}") 
    AND password = "{password}"  LIMIT 1;"""
    ret = conn.execute(query)
    det = ret.fetchone()
    if det is not None:
        user_details = {"acc_no": det[0], "name": det[2], "role": det[8]}
        prefix = ""
        if det[5] == "M":
            prefix = "Mr. "
        elif det[5] == "F":
            prefix = "Mrs. "
        user_details.update({"prefix": prefix})

        last_login_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        if user_details["role"]:
            openAccountDetailsPage()

    else:
        # show the error message
        show_message_box(msg_type="error", msg="Invalid credentials")
    conn.close()


def logout():
    global user_details, last_login_time

    user_details = None
    last_login_time = None
    openIntroPage()


def updateWithdrawlAmount(val: str):
    amount = main_win.hldr_wdrl.label_9.text()

    if amount == "Enter Amount to Withdrawl":
        amount = ""

    if val == "-2":
        amount = "Enter Amount to Withdrawl"
    elif val == "-1":
        amount = amount[:-1]
    elif "." in amount and val == ".":
        pass
    elif "." in amount and len(amount) - amount.find(".") == 3:
        pass
    else:
        amount += val
    main_win.hldr_wdrl.label_9.setText(amount)


def selfWithdrawl():
    try:
        amount = float(main_win.hldr_wdrl.label_9.text())
    except ValueError:
        # show the error message
        show_message_box(msg_type="error", msg="Enter a valid amount")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {user_details["acc_no"]} LIMIT 1;"""
    ret = conn.execute(query)
    data = ret.fetchone()
    conn.close()

    if data[9] < amount:
        # show the error message
        show_message_box(msg_type="error", msg="Insufficient Balance")
        return
    avail_bal = data[9] - amount

    timestamp = str(datetime.now())
    conn = sql.Connection(DB_PATH)
    query = f"""INSERT INTO Transactions(acc_no, timestamp, operation, prev_bal, trans_amount, avail_bal, 
    operation_details, operator) VALUES({user_details["acc_no"]}, "{timestamp}", "Db", {data[9]}, {amount}, {avail_bal}, 
    "Withdrawl from ATM", {user_details["acc_no"]});"""
    conn.execute(query)
    query = f"""UPDATE AccountDetails SET curr_bal = {avail_bal} WHERE acc_no = {user_details["acc_no"]};"""
    conn.execute(query)
    conn.commit()
    conn.close()

    show_message_box(msg=f"Transaction successful\nAvailable Balance: {avail_bal}")
    openCustomerWithdrawlPage()


def showCustomerTrans():
    main_win.customer_trans.tableWidget.setRowCount(0)

    from_dt = main_win.customer_trans.dateEdit.date().toString("yyyy-MM-dd")
    to_dt = main_win.customer_trans.dateEdit_2.date().toString("yyyy-MM-dd")
    to_dt += " 23:59:59"

    py_from_dt = datetime.strptime(from_dt, "%Y-%m-%d")
    py_to_dt = datetime.strptime(to_dt, "%Y-%m-%d %H:%M:%S")

    if py_from_dt > py_to_dt:
        # show the error message
        show_message_box(msg_type="error", msg="From date can not exceed to date")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM Transactions WHERE acc_no = {user_details["acc_no"]} AND datetime(timestamp)
    BETWEEN datetime("{py_from_dt}") AND datetime("{py_to_dt}");"""
    ret = conn.execute(query)
    data = ret.fetchall()
    conn.close()

    if not data:
        # show the error message
        show_message_box(msg_type="error", msg="No Transactions found")
        return

    for row in data:
        currentRow = main_win.customer_trans.tableWidget.rowCount()
        main_win.customer_trans.tableWidget.setRowCount(currentRow + 1)
        main_win.customer_trans.tableWidget.setItem(
            currentRow, 0, QTableWidgetItem(str(row[2])[:10])
        )
        main_win.customer_trans.tableWidget.setItem(
            currentRow, 1, QTableWidgetItem(str(row[7]))
        )
        main_win.customer_trans.tableWidget.setItem(
            currentRow, 2, QTableWidgetItem(str(row[5]))
        )
        main_win.customer_trans.tableWidget.setItem(
            currentRow, 3, QTableWidgetItem(str(row[3]))
        )
        main_win.customer_trans.tableWidget.setItem(
            currentRow, 4, QTableWidgetItem(str(row[6]))
        )

    return data


def printCustomerTrans():
    data = showCustomerTrans()

    if not data:
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {user_details["acc_no"]} LIMIT 1;"""
    ret = conn.execute(query)
    user_data = ret.fetchone()
    conn.close()

    generate_report(
        user_data,
        data,
        main_win.customer_trans.dateEdit.date().toString("yyyy-MM-dd"),
        main_win.customer_trans.dateEdit_2.date().toString("yyyy-MM-dd"),
    )


def fetchCustomerDetails(page: str):
    acc_no = 0

    if page == "D":
        acc_no = main_win.swo_dep.lineEdit.text()
    elif page == "W":
        acc_no = main_win.swo_wdrl.lineEdit.text()
    elif page == "TMS":
        acc_no = main_win.swo_tf_mn.lineEdit.text()
        if not validate_account_no(acc_no) or not validate_account_no(
            main_win.swo_tf_mn.lineEdit_2.text()
        ):
            show_message_box(
                msg_type="error", msg="Both Account Number should be valid"
            )
            return
    elif page == "TMR":
        acc_no = main_win.swo_tf_mn.lineEdit_2.text()
        if not validate_account_no(acc_no) or not validate_account_no(
            main_win.swo_tf_mn.lineEdit.text()
        ):
            return
    elif page == "T":
        acc_no = main_win.swo_trans.lineEdit.text()

    if not validate_account_no(acc_no) and page not in ["TMS", "TMR"]:
        # show the error message
        show_message_box(msg_type="error", msg="Invalid Account Number")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {acc_no} LIMIT 1;"""
    ret = conn.execute(query)
    data = ret.fetchone()
    conn.close()

    cust_name = ""
    cust_mobile = ""
    avail_bal = 0
    if data is not None:
        prefix = ""
        if data[5] == "M":
            prefix = "Mr. "
        elif data[5] == "F":
            prefix = "Mrs. "
        cust_name += prefix
        cust_name += data[2]
        cust_mobile = data[4]
        avail_bal = float(data[9])

        if page == "D":
            main_win.swo_dep.label_10.setText(cust_name)
            main_win.swo_dep.label_11.setText(cust_mobile)
            main_win.swo_dep.label_14.setText(f"₹{avail_bal:.2f}")
        elif page == "W":
            main_win.swo_wdrl.label_10.setText(cust_name)
            main_win.swo_wdrl.label_11.setText(cust_mobile)
            main_win.swo_wdrl.label_14.setText(f"₹{avail_bal:.2f}")
        elif page == "TMS":
            main_win.swo_tf_mn.label_10.setText(cust_name)
            main_win.swo_tf_mn.label_11.setText(cust_mobile)
            main_win.swo_tf_mn.label_14.setText(f"₹{avail_bal:.2f}")
        elif page == "TMR":
            main_win.swo_tf_mn.label_16.setText(cust_name)
        elif page == "T":
            main_win.swo_trans.label_12.setText(cust_name)

    else:
        if page == "D":
            openSWO_DepositPage()
        elif page == "W":
            openSWO_WithdrawlPage()
        elif page == "TMS":
            openSWO_TransferPage()
        elif page == "TMR":
            openSWO_TransferPage()
        elif page == "T":
            openSWO_TransPage()
        # show the error message
        show_message_box(msg_type="error", msg="Account Not Found")


def officeDeposit():
    acc_no = main_win.swo_dep.lineEdit.text()
    holder_name = main_win.swo_dep.label_10.text()
    dep_amt = main_win.swo_dep.spinBox.value()

    if not validate_account_no(acc_no):
        # show the error message
        show_message_box(msg_type="error", msg="Invalid Account Number")
        return

    if not holder_name:
        # show the error message
        show_message_box(msg_type="error", msg="Check out holder details first")
        return

    if user_details["acc_no"] == int(acc_no):
        # show the error message
        show_message_box(msg_type="error", msg="Transaction not allowed for self")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {acc_no} LIMIT 1;"""
    ret = conn.execute(query)
    data = ret.fetchone()
    conn.close()

    if not data:
        # show the error message
        show_message_box(msg_type="error", msg="Account not found")
        openSWO_DepositPage()
        main_win.swo_dep.lineEdit.setText(str(acc_no))
        return
    else:
        fetchCustomerDetails("D")

    avail_bal = data[9] + dep_amt

    timestamp = str(datetime.now())
    conn = sql.Connection(DB_PATH)
    query = f"""INSERT INTO Transactions(acc_no, timestamp, operation, prev_bal, trans_amount, avail_bal, 
    operation_details, operator) VALUES({acc_no}, "{timestamp}", "Cr", {data[9]}, {dep_amt}, {avail_bal}, 
    "Deposit at Bank", {user_details["acc_no"]});"""
    conn.execute(query)
    query = (
        f"""UPDATE AccountDetails SET curr_bal = {avail_bal} WHERE acc_no = {acc_no};"""
    )
    conn.execute(query)
    conn.commit()
    conn.close()

    show_message_box(msg=f"Transaction successful\nAvailable Balance: {avail_bal}")
    openSWO_DepositPage()


def officeWithdrawl():
    acc_no = main_win.swo_wdrl.lineEdit.text()
    holder_name = main_win.swo_wdrl.label_10.text()
    wdrl_amt = main_win.swo_wdrl.spinBox.value()

    if not validate_account_no(acc_no):
        # show the error message
        show_message_box(msg_type="error", msg="Invalid Account Number")
        return

    if not holder_name:
        # show the error message
        show_message_box(msg_type="error", msg="Check out holder details first")
        return

    if user_details["acc_no"] == int(acc_no):
        # show the error message
        show_message_box(msg_type="error", msg="Transaction not allowed for self")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {acc_no} LIMIT 1;"""
    ret = conn.execute(query)
    data = ret.fetchone()
    conn.close()

    if not data:
        # show the error message
        show_message_box(msg_type="error", msg="Account not found")
        openSWO_WithdrawlPage()
        main_win.swo_wdrl.lineEdit.setText(str(acc_no))
        return
    else:
        fetchCustomerDetails("W")

    if data[9] < wdrl_amt:
        # show the error message
        show_message_box(msg_type="error", msg="Insufficient Balance")
        return
    avail_bal = data[9] - wdrl_amt

    timestamp = str(datetime.now())
    conn = sql.Connection(DB_PATH)
    query = f"""INSERT INTO Transactions(acc_no, timestamp, operation, prev_bal, trans_amount, avail_bal, 
    operation_details, operator) VALUES({acc_no}, "{timestamp}", "Db", {data[9]}, {wdrl_amt}, {avail_bal}, 
    "Withdrawl at Bank", {user_details["acc_no"]});"""
    conn.execute(query)
    query = (
        f"""UPDATE AccountDetails SET curr_bal = {avail_bal} WHERE acc_no = {acc_no};"""
    )
    conn.execute(query)
    conn.commit()
    conn.close()

    show_message_box(msg=f"Transaction successful\nAvailable Balance: {avail_bal}")
    openSWO_WithdrawlPage()


def officeTransfer():
    sender_acc_no = main_win.swo_tf_mn.lineEdit.text()
    receiver_acc_no = main_win.swo_tf_mn.lineEdit_2.text()
    sender_name = main_win.swo_tf_mn.label_10.text()
    receiver_name = main_win.swo_tf_mn.label_16.text()
    transfer_amt = main_win.swo_tf_mn.spinBox.value()

    if not validate_account_no(sender_acc_no) or not validate_account_no(
        receiver_acc_no
    ):
        # show the error message
        show_message_box(msg_type="error", msg="Both Account Number should be valid")
        return

    if not sender_name or not receiver_name:
        # show the error message
        show_message_box(msg_type="error", msg="Check out holder details first")
        return

    if user_details["acc_no"] == int(sender_acc_no):
        # show the error message
        show_message_box(msg_type="error", msg="Transaction not allowed for self")
        return

    if int(sender_acc_no) == int(receiver_acc_no):
        # show the error message
        show_message_box(msg_type="error", msg="Can not transfer to same account")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {sender_acc_no} LIMIT 1;"""
    ret = conn.execute(query)
    sender_data = ret.fetchone()
    conn.close()

    if not sender_data:
        # show the error message
        show_message_box(msg_type="error", msg="Sender account not found")
        openSWO_TransferPage()
        main_win.swo_tf_mn.lineEdit.setText(str(sender_acc_no))
        main_win.swo_tf_mn.lineEdit_2.setText(str(receiver_acc_no))
        return
    else:
        fetchCustomerDetails("TMS")

    conn = sql.Connection(DB_PATH)
    query = (
        f"""SELECT * FROM AccountDetails WHERE acc_no = {receiver_acc_no} LIMIT 1;"""
    )
    ret = conn.execute(query)
    receiver_data = ret.fetchone()
    conn.close()

    if not receiver_data:
        # show the error message
        show_message_box(msg_type="error", msg="Receiver account not found")
        openSWO_TransferPage()
        main_win.swo_tf_mn.lineEdit.setText(str(sender_acc_no))
        main_win.swo_tf_mn.lineEdit_2.setText(str(receiver_acc_no))
        return
    else:
        fetchCustomerDetails("TMR")

    if sender_data[9] < transfer_amt:
        # show the error message
        show_message_box(msg_type="error", msg="Insufficient Balance")
        return

    sender_avail_bal = sender_data[9] - transfer_amt
    receiver_avail_bal = receiver_data[9] + transfer_amt

    timestamp = str(datetime.now())
    conn = sql.Connection(DB_PATH)
    query = f"""INSERT INTO Transactions(acc_no, timestamp, operation, prev_bal, trans_amount, avail_bal, 
    operation_details, operator) VALUES({sender_acc_no}, "{timestamp}", "Db", {sender_data[9]}, {transfer_amt}, 
    {sender_avail_bal}, "Transferred to {receiver_acc_no}", {user_details["acc_no"]});"""
    conn.execute(query)
    query = f"""UPDATE AccountDetails SET curr_bal = {sender_avail_bal} WHERE acc_no = {sender_acc_no};"""
    conn.execute(query)
    query = f"""INSERT INTO Transactions(acc_no, timestamp, operation, prev_bal, trans_amount, avail_bal, 
    operation_details, operator) VALUES({receiver_acc_no}, "{timestamp}", "Cr", {receiver_data[9]}, {transfer_amt}, 
    {receiver_avail_bal}, "Transferred from {sender_acc_no}", {user_details["acc_no"]});"""
    conn.execute(query)
    query = f"""UPDATE AccountDetails SET curr_bal = {receiver_avail_bal} WHERE acc_no = {receiver_acc_no};"""
    conn.execute(query)
    conn.commit()
    conn.close()

    show_message_box(
        msg=f"Transaction successful\nAvailable Balance: {sender_avail_bal}"
    )
    openSWO_TransferPage()


def officeTrans():
    openSWO_TransPage()

    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM Transactions WHERE operator = {user_details["acc_no"]} AND datetime(timestamp)
    BETWEEN datetime("{start_of_day}") AND datetime("{end_of_day}");"""
    ret = conn.execute(query)
    data = ret.fetchall()
    conn.close()

    if not data:
        # show the error message
        show_message_box(msg_type="error", msg="No transactions found for today")
        return

    cr_val = 0
    db_val = 0
    for row in data:
        currentRow = main_win.swo_trans.tableWidget.rowCount()
        main_win.swo_trans.tableWidget.setRowCount(currentRow + 1)
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 0, QTableWidgetItem(str(row[2])[:10])
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 1, QTableWidgetItem(str(row[7]))
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 2, QTableWidgetItem(str(row[5]))
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 3, QTableWidgetItem(str(row[3]))
        )
        main_win.swo_trans.tableWidget.setItem(currentRow, 4, QTableWidgetItem(""))

        if row[3] == "Cr":
            cr_val += row[5]
        elif row[3] == "Db":
            db_val += row[5]

    currentRow = main_win.swo_trans.tableWidget.rowCount()
    main_win.swo_trans.tableWidget.setRowCount(currentRow + 1)
    main_win.swo_trans.tableWidget.setItem(currentRow, 0, QTableWidgetItem(""))
    main_win.swo_trans.tableWidget.setItem(
        currentRow, 1, QTableWidgetItem("Total Transaction")
    )
    main_win.swo_trans.tableWidget.setItem(
        currentRow, 2, QTableWidgetItem(str(cr_val + db_val))
    )
    main_win.swo_trans.tableWidget.setItem(currentRow, 3, QTableWidgetItem(""))
    main_win.swo_trans.tableWidget.setItem(currentRow, 4, QTableWidgetItem(""))

    currentRow = main_win.swo_trans.tableWidget.rowCount()
    main_win.swo_trans.tableWidget.setRowCount(currentRow + 1)
    main_win.swo_trans.tableWidget.setItem(currentRow, 0, QTableWidgetItem(""))
    main_win.swo_trans.tableWidget.setItem(
        currentRow, 1, QTableWidgetItem("Floating Amount")
    )
    main_win.swo_trans.tableWidget.setItem(
        currentRow, 2, QTableWidgetItem(str(cr_val - db_val))
    )
    main_win.swo_trans.tableWidget.setItem(currentRow, 3, QTableWidgetItem(""))
    main_win.swo_trans.tableWidget.setItem(currentRow, 4, QTableWidgetItem(""))


def customerTrans():
    fetchCustomerDetails("T")
    main_win.swo_trans.tableWidget.setRowCount(0)

    if not main_win.swo_trans.label_12.text():
        return

    acc_no = main_win.swo_trans.lineEdit.text()

    from_dt = main_win.swo_trans.dateEdit.date().toString("yyyy-MM-dd")
    to_dt = main_win.swo_trans.dateEdit_2.date().toString("yyyy-MM-dd")
    to_dt += " 23:59:59"

    py_from_dt = datetime.strptime(from_dt, "%Y-%m-%d")
    py_to_dt = datetime.strptime(to_dt, "%Y-%m-%d %H:%M:%S")

    if py_from_dt > py_to_dt:
        # show the error message
        show_message_box(msg_type="error", msg="From date can not exceed to date")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM Transactions WHERE acc_no = {acc_no} AND datetime(timestamp)
    BETWEEN datetime("{py_from_dt}") AND datetime("{py_to_dt}");"""
    ret = conn.execute(query)
    data = ret.fetchall()
    conn.close()

    if not data:
        # show the error message
        show_message_box(msg_type="error", msg="No Transactions found")
        return

    for row in data:
        currentRow = main_win.swo_trans.tableWidget.rowCount()
        main_win.swo_trans.tableWidget.setRowCount(currentRow + 1)
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 0, QTableWidgetItem(str(row[2])[:10])
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 1, QTableWidgetItem(str(row[7]))
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 2, QTableWidgetItem(str(row[5]))
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 3, QTableWidgetItem(str(row[3]))
        )
        main_win.swo_trans.tableWidget.setItem(
            currentRow, 4, QTableWidgetItem(str(row[6]))
        )

    return data


def printCustomerTransFromSWO():
    data = customerTrans()

    if not data:
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {main_win.swo_trans.lineEdit.text()} LIMIT 1;"""
    ret = conn.execute(query)
    user_data = ret.fetchone()
    conn.close()

    generate_report(
        user_data,
        data,
        main_win.swo_trans.dateEdit.date().toString("yyyy-MM-dd"),
        main_win.swo_trans.dateEdit_2.date().toString("yyyy-MM-dd"),
    )


def addCustomer():
    cust_name = main_win.admin_new_user.lineEdit.text()
    cust_email = main_win.admin_new_user.lineEdit_2.text()
    cust_mobile = main_win.admin_new_user.lineEdit_3.text()
    cust_gender = main_win.admin_new_user.comboBox.currentText()
    cust_dob = main_win.admin_new_user.dateEdit.date().toString("yyyy-MM-dd")
    acc_type = main_win.admin_new_user.comboBox_2.currentText()
    open_bal = main_win.admin_new_user.spinBox.value()
    cust_pwd = main_win.admin_new_user.lineEdit_4.text()

    ret, err_msg = validate_fullname(cust_name)
    if not ret:
        show_message_box(msg_type="error", msg=err_msg)
        return

    if not validate_email(cust_email):
        show_message_box(msg_type="error", msg="Please provide a valid mail")
        return

    if not validate_mobile(cust_mobile):
        show_message_box(msg_type="error", msg="Please provide a valid mobile number")
        return

    if cust_gender == "Male":
        cust_gender = "M"
    elif cust_gender == "Female":
        cust_gender = "F"
    else:
        cust_gender = "O"

    if acc_type == "Current":
        acc_type = "C"
    else:
        acc_type = "S"

    ret, err_msg = validate_password(cust_pwd)
    if not ret:
        show_message_box(msg_type="error", msg=err_msg)
        return

    conn = sql.Connection(DB_PATH)
    try:
        # Add information to DB
        query = f"""INSERT INTO AccountDetails(acc_type, full_name, email, mobile, gender, dob, password, user_type, 
        curr_bal) VALUES("{acc_type}", "{cust_name}", "{cust_email}", "{cust_mobile}", "{cust_gender}", 
        "{cust_dob}", "{encrypt_password(cust_pwd)}", "C", {open_bal});"""
        conn.execute(query)
        query = "SELECT last_insert_rowid()"
        ret = conn.execute(query)
        cust_acc_no = ret.fetchone()[0]
        timestamp = str(datetime.now())
        query = f"""INSERT INTO Transactions(acc_no, timestamp, operation, prev_bal, trans_amount, avail_bal, 
        operation_details, operator) VALUES({cust_acc_no}, "{timestamp}", "Cr", 0.0, {open_bal}, {open_bal}, 
        "Account opening balance", {user_details["acc_no"]});"""
        conn.execute(query)
        conn.commit()
    except sql.IntegrityError as err:
        if "AccountDetails.mobile" in str(err):
            show_message_box(msg_type="error", msg="Mobile number already exists")
        if "AccountDetails.email" in str(err):
            show_message_box(msg_type="error", msg="Email already exists")
    else:
        openNewCustomerPage()
        show_message_box(
            msg=f"Customer Account created\nAccount No. {cust_acc_no}\nPassword: {cust_pwd}"
        )
    conn.close()


def fetchKYCdata():
    acc_no = main_win.admin_update.lineEdit.text()
    if len(acc_no) < 6:
        return

    if not validate_account_no(acc_no):
        openKYC_Page(clear_acc_no=False)
        # show the error message
        show_message_box(msg_type="error", msg="Invalid Account Number")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {acc_no} LIMIT 1"""
    ret = conn.execute(query)
    data = ret.fetchone()
    conn.close()

    if data is None:
        openKYC_Page(clear_acc_no=False)
        return

    main_win.admin_update.lineEdit_2.setText(data[2])
    main_win.admin_update.lineEdit_3.setText(data[3])
    main_win.admin_update.lineEdit_4.setText(data[4])
    main_win.admin_update.lineEdit_5.setText("")

    gender_index = None
    if data[5] == "M":
        gender_index = 0
    elif data[5] == "F":
        gender_index = 1
    elif data[5] == "O":
        gender_index = 2
    main_win.admin_update.comboBox.setCurrentIndex(gender_index)

    acc_type_index = None
    if data[1] == "C":
        acc_type_index = 0
    elif data[1] == "S":
        acc_type_index = 1
    main_win.admin_update.comboBox_2.setCurrentIndex(acc_type_index)

    user_type_index = None
    if data[8] == "A":
        user_type_index = 0
    elif data[8] == "C":
        user_type_index = 1
    elif data[8] == "S":
        user_type_index = 2
    main_win.admin_update.comboBox_3.setCurrentIndex(user_type_index)

    main_win.admin_update.dateEdit.setDate(QDate.fromString(data[6], "yyyy-MM-dd"))


def fetchKYCdataWithError():
    fetchKYCdata()
    if not main_win.admin_update.lineEdit_2.text():
        show_message_box(msg_type="error", msg="Account not found")


def updateKYC():
    global user_details

    acc_no = main_win.admin_update.lineEdit.text()
    if not validate_account_no(acc_no):
        openKYC_Page(clear_acc_no=False)
        # show the error message
        show_message_box(msg_type="error", msg="Invalid Account Number")
        return

    cust_name = main_win.admin_update.lineEdit_2.text()
    cust_email = main_win.admin_update.lineEdit_3.text()
    cust_mobile = main_win.admin_update.lineEdit_4.text()
    cust_gender = main_win.admin_update.comboBox.currentText()
    cust_dob = main_win.admin_update.dateEdit.date().toString("yyyy-MM-dd")
    acc_type = main_win.admin_update.comboBox_2.currentText()
    user_type = main_win.admin_update.comboBox_3.currentText()
    cust_pwd = main_win.admin_update.lineEdit_5.text()

    ret, err_msg = validate_fullname(cust_name)
    if not ret:
        show_message_box(msg_type="error", msg=err_msg)
        return

    if not validate_email(cust_email):
        show_message_box(msg_type="error", msg="Please provide a valid mail")
        return

    if not validate_mobile(cust_mobile):
        show_message_box(msg_type="error", msg="Please provide a valid mobile number")
        return

    if cust_gender == "Male":
        cust_gender = "M"
    elif cust_gender == "Female":
        cust_gender = "F"
    else:
        cust_gender = "O"

    if acc_type == "Current":
        acc_type = "C"
    else:
        acc_type = "S"

    if user_type == "Admin":
        user_type = "A"
    elif user_type == "Customer":
        user_type = "C"
    else:
        user_type = "S"

    ret, err_msg = validate_password(cust_pwd)
    if not ret:
        show_message_box(msg_type="error", msg=err_msg)
        return

    conn = sql.Connection(DB_PATH)
    try:
        query = f"""UPDATE AccountDetails SET acc_type = "{acc_type}", full_name = "{cust_name}", 
        email = "{cust_email}", mobile = "{cust_mobile}", gender = "{cust_gender}", dob = "{cust_dob}", 
        password = "{encrypt_password(cust_pwd)}", user_type = "{user_type}" WHERE acc_no = {acc_no};"""
        conn.execute(query)
        conn.commit()
    except sql.IntegrityError as err:
        if "AccountDetails.mobile" in str(err):
            show_message_box(msg_type="error", msg="Mobile number already exists")
        if "AccountDetails.email" in str(err):
            show_message_box(msg_type="error", msg="Email already exists")
    else:
        openKYC_Page()
        show_message_box(msg="Customer Details Updated")
    conn.close()

    if acc_no == user_details["acc_no"]:
        conn = sql.Connection(DB_PATH)
        query = f"""SELECT * FROM AccountDetails WHERE acc_no = {acc_no}  LIMIT 1;"""
        ret = conn.execute(query)
        det = ret.fetchone()
        if det is not None:
            user_details = {"acc_no": det[0], "name": det[2], "role": det[8]}
            prefix = ""
            if det[5] == "M":
                prefix = "Mr. "
            elif det[5] == "F":
                prefix = "Mrs. "
            user_details.update({"prefix": prefix})
        conn.close()


def showEmployeeTransactions():
    main_win.admin_trans.tableWidget.setRowCount(0)

    acc_no = main_win.admin_trans.lineEdit.text()

    if not validate_account_no(acc_no):
        show_message_box(msg_type="error", msg="Invalid Account Number")
        return

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM AccountDetails WHERE acc_no = {acc_no}  LIMIT 1;"""
    ret = conn.execute(query)
    user_data = ret.fetchone()
    conn.close()

    if user_data and user_data[8] in ["A", "S"]:
        pass
    else:
        show_message_box(
            msg_type="error",
            msg="Only employees (Admin/SWO) transanctions can be checked here",
        )
        return

    from_dt = main_win.admin_trans.dateEdit.date().toString("yyyy-MM-dd")
    to_dt = main_win.admin_trans.dateEdit_2.date().toString("yyyy-MM-dd")
    to_dt += " 23:59:59"

    py_from_dt = datetime.strptime(from_dt, "%Y-%m-%d")
    py_to_dt = datetime.strptime(to_dt, "%Y-%m-%d %H:%M:%S")

    if py_from_dt > py_to_dt:
        # show the error message
        show_message_box(msg_type="error", msg="From date can not exceed to date")
        return

    main_win.admin_trans.label_12.setText(user_data[2])

    conn = sql.Connection(DB_PATH)
    query = f"""SELECT * FROM Transactions WHERE operator = {acc_no} AND datetime(timestamp)
    BETWEEN datetime("{py_from_dt}") AND datetime("{py_to_dt}");"""
    ret = conn.execute(query)
    data = ret.fetchall()
    conn.close()

    if not data:
        # show the error message
        show_message_box(msg_type="error", msg="No transactions found for today")
        return

    cr_val = 0
    db_val = 0
    for row in data:
        currentRow = main_win.admin_trans.tableWidget.rowCount()
        main_win.admin_trans.tableWidget.setRowCount(currentRow + 1)
        main_win.admin_trans.tableWidget.setItem(
            currentRow, 0, QTableWidgetItem(str(row[2])[:10])
        )
        main_win.admin_trans.tableWidget.setItem(
            currentRow, 1, QTableWidgetItem(str(row[7]))
        )
        main_win.admin_trans.tableWidget.setItem(
            currentRow, 2, QTableWidgetItem(str(row[5]))
        )
        main_win.admin_trans.tableWidget.setItem(
            currentRow, 3, QTableWidgetItem(str(row[3]))
        )

        if row[3] == "Cr":
            cr_val += row[5]
        elif row[3] == "Db":
            db_val += row[5]

    currentRow = main_win.admin_trans.tableWidget.rowCount()
    main_win.admin_trans.tableWidget.setRowCount(currentRow + 1)
    main_win.admin_trans.tableWidget.setItem(currentRow, 0, QTableWidgetItem(""))
    main_win.admin_trans.tableWidget.setItem(
        currentRow, 1, QTableWidgetItem("Total Transaction")
    )
    main_win.admin_trans.tableWidget.setItem(
        currentRow, 2, QTableWidgetItem(str(cr_val + db_val))
    )
    main_win.admin_trans.tableWidget.setItem(currentRow, 3, QTableWidgetItem(""))

    currentRow = main_win.admin_trans.tableWidget.rowCount()
    main_win.admin_trans.tableWidget.setRowCount(currentRow + 1)
    main_win.admin_trans.tableWidget.setItem(currentRow, 0, QTableWidgetItem(""))
    main_win.admin_trans.tableWidget.setItem(
        currentRow, 1, QTableWidgetItem("Floating Amount")
    )
    main_win.admin_trans.tableWidget.setItem(
        currentRow, 2, QTableWidgetItem(str(cr_val - db_val))
    )
    main_win.admin_trans.tableWidget.setItem(currentRow, 3, QTableWidgetItem(""))

    return user_data, data


def printTransactions():
    data = showEmployeeTransactions()

    if not data:
        return

    user_data, data = data
    generate_report(
        user_data,
        data,
        main_win.admin_trans.dateEdit.date().toString("yyyy-MM-dd"),
        main_win.admin_trans.dateEdit_2.date().toString("yyyy-MM-dd"),
        is_emp=True,
    )


###############################   Main Program   ##############################
if __name__ == "__main__":
    # Verify database
    initial_db_check()

    # Configure application
    if hasattr(QtCore.Qt, "AA_EnableHighDepiScaling"):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication([])

    # https://stackoverflow.com/questions/67599432/setting-the-same-icon-as-application-icon-in-task-bar-for-pyqt5-application
    MY_APP_ID = "cttc.mb.v2.0.0"  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(MY_APP_ID)

    main_win = MainWindow()
    main_win.setWindowIcon(QIcon(resource_path("assets\\images\\Mo Bank logo.jpg")))
    main_win.show()

    main_win.intro.pushButton.clicked.connect(openLoginPage)
    main_win.intro.pushButton_2.clicked.connect(openGithubRepo)
    main_win.intro.pushButton_3.clicked.connect(openGithubProfile)

    main_win.login.pushButton.clicked.connect(completeLogin)
    main_win.login.pushButton_2.clicked.connect(openIntroPage)

    main_win.acc_det.pushButton_2.clicked.connect(logout)
    main_win.acc_det.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.acc_det.pushButton_4.clicked.connect(openSWO_DepositPage)
    main_win.acc_det.pushButton_7.clicked.connect(openCustomerWithdrawlPage)
    main_win.acc_det.pushButton_8.clicked.connect(openCustomerTransPage)

    main_win.hldr_wdrl.pushButton_2.clicked.connect(logout)
    main_win.hldr_wdrl.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.hldr_wdrl.pushButton_4.clicked.connect(openSWO_DepositPage)
    main_win.hldr_wdrl.pushButton_6.clicked.connect(openAccountDetailsPage)
    main_win.hldr_wdrl.pushButton_8.clicked.connect(openCustomerTransPage)
    main_win.hldr_wdrl.pushButton.clicked.connect(partial(updateWithdrawlAmount, "1"))
    main_win.hldr_wdrl.pushButton_9.clicked.connect(partial(updateWithdrawlAmount, "2"))
    main_win.hldr_wdrl.pushButton_10.clicked.connect(
        partial(updateWithdrawlAmount, "3")
    )
    main_win.hldr_wdrl.pushButton_11.clicked.connect(
        partial(updateWithdrawlAmount, "4")
    )
    main_win.hldr_wdrl.pushButton_12.clicked.connect(
        partial(updateWithdrawlAmount, "5")
    )
    main_win.hldr_wdrl.pushButton_13.clicked.connect(
        partial(updateWithdrawlAmount, "6")
    )
    main_win.hldr_wdrl.pushButton_14.clicked.connect(
        partial(updateWithdrawlAmount, "7")
    )
    main_win.hldr_wdrl.pushButton_15.clicked.connect(
        partial(updateWithdrawlAmount, "8")
    )
    main_win.hldr_wdrl.pushButton_16.clicked.connect(
        partial(updateWithdrawlAmount, "9")
    )
    main_win.hldr_wdrl.pushButton_17.clicked.connect(
        partial(updateWithdrawlAmount, ".")
    )
    main_win.hldr_wdrl.pushButton_18.clicked.connect(
        partial(updateWithdrawlAmount, "0")
    )
    main_win.hldr_wdrl.pushButton_19.clicked.connect(
        partial(updateWithdrawlAmount, "-1")
    )
    main_win.hldr_wdrl.pushButton_20.clicked.connect(selfWithdrawl)
    main_win.hldr_wdrl.pushButton_21.clicked.connect(
        partial(updateWithdrawlAmount, "-2")
    )

    main_win.customer_trans.pushButton.clicked.connect(showCustomerTrans)
    main_win.customer_trans.pushButton_2.clicked.connect(logout)
    main_win.customer_trans.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.customer_trans.pushButton_4.clicked.connect(openSWO_DepositPage)
    main_win.customer_trans.pushButton_6.clicked.connect(openAccountDetailsPage)
    main_win.customer_trans.pushButton_7.clicked.connect(openCustomerWithdrawlPage)
    main_win.customer_trans.pushButton_10.clicked.connect(printCustomerTrans)

    main_win.swo_dep.pushButton.clicked.connect(officeDeposit)
    main_win.swo_dep.pushButton_2.clicked.connect(logout)
    main_win.swo_dep.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.swo_dep.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.swo_dep.pushButton_7.clicked.connect(openSWO_WithdrawlPage)
    main_win.swo_dep.pushButton_8.clicked.connect(openSWO_TransferPage)
    main_win.swo_dep.pushButton_9.clicked.connect(openSWO_TransPage)
    main_win.swo_dep.pushButton_10.clicked.connect(partial(fetchCustomerDetails, "D"))

    main_win.swo_wdrl.pushButton.clicked.connect(officeWithdrawl)
    main_win.swo_wdrl.pushButton_2.clicked.connect(logout)
    main_win.swo_wdrl.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.swo_wdrl.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.swo_wdrl.pushButton_6.clicked.connect(openSWO_DepositPage)
    main_win.swo_wdrl.pushButton_8.clicked.connect(openSWO_TransferPage)
    main_win.swo_wdrl.pushButton_9.clicked.connect(openSWO_TransPage)
    main_win.swo_wdrl.pushButton_10.clicked.connect(partial(fetchCustomerDetails, "W"))

    main_win.swo_tf_mn.pushButton.clicked.connect(officeTransfer)
    main_win.swo_tf_mn.pushButton_2.clicked.connect(logout)
    main_win.swo_tf_mn.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.swo_tf_mn.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.swo_tf_mn.pushButton_6.clicked.connect(openSWO_DepositPage)
    main_win.swo_tf_mn.pushButton_7.clicked.connect(openSWO_WithdrawlPage)
    main_win.swo_tf_mn.pushButton_9.clicked.connect(openSWO_TransPage)
    main_win.swo_tf_mn.pushButton_10.clicked.connect(
        partial(fetchCustomerDetails, "TMS")
    )
    main_win.swo_tf_mn.pushButton_10.clicked.connect(
        partial(fetchCustomerDetails, "TMR")
    )

    main_win.swo_trans.pushButton.clicked.connect(officeTrans)
    main_win.swo_trans.pushButton_2.clicked.connect(logout)
    main_win.swo_trans.pushButton_3.clicked.connect(openNewCustomerPage)
    main_win.swo_trans.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.swo_trans.pushButton_6.clicked.connect(openSWO_DepositPage)
    main_win.swo_trans.pushButton_7.clicked.connect(openSWO_WithdrawlPage)
    main_win.swo_trans.pushButton_8.clicked.connect(openSWO_TransferPage)
    main_win.swo_trans.pushButton_10.clicked.connect(customerTrans)
    main_win.swo_trans.pushButton_11.clicked.connect(printCustomerTransFromSWO)

    main_win.admin_new_user.pushButton.clicked.connect(addCustomer)
    main_win.admin_new_user.pushButton_2.clicked.connect(logout)
    main_win.admin_new_user.pushButton_4.clicked.connect(openSWO_DepositPage)
    main_win.admin_new_user.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.admin_new_user.pushButton_7.clicked.connect(partial(openKYC_Page, True))
    main_win.admin_new_user.pushButton_8.clicked.connect(openTransactionPage)

    main_win.admin_update.pushButton.clicked.connect(updateKYC)
    main_win.admin_update.pushButton_2.clicked.connect(logout)
    main_win.admin_update.pushButton_4.clicked.connect(openSWO_DepositPage)
    main_win.admin_update.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.admin_update.pushButton_6.clicked.connect(openNewCustomerPage)
    main_win.admin_update.pushButton_8.clicked.connect(openTransactionPage)
    main_win.admin_update.lineEdit.textChanged.connect(fetchKYCdata)
    main_win.admin_update.pushButton_9.clicked.connect(fetchKYCdataWithError)

    main_win.admin_trans.pushButton.clicked.connect(showEmployeeTransactions)
    main_win.admin_trans.pushButton_2.clicked.connect(logout)
    main_win.admin_trans.pushButton_4.clicked.connect(openSWO_DepositPage)
    main_win.admin_trans.pushButton_5.clicked.connect(openAccountDetailsPage)
    main_win.admin_trans.pushButton_6.clicked.connect(openNewCustomerPage)
    main_win.admin_trans.pushButton_7.clicked.connect(partial(openKYC_Page, True))
    main_win.admin_trans.pushButton_9.clicked.connect(printTransactions)

    app.exec()
    app.quit()

    # delete the application
    del app
