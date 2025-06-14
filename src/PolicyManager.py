import os
import sys
import pandas as pd
import datetime as datetime
from tabulate import tabulate
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from dateutil.relativedelta import relativedelta
from AddPolicy import AddPolicy


LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))

Frequency_dict = {'Monthly': 1, 'Quarterly': 3, 'Half Yearly': 6, 'Yearly': 12}


def close_cliked():
    print('Exiting')
    exit(0)


def prompt_user(msg_title, msg_str, msg_type='Info'):
    pass

class Main(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(LOCAL_DIR + "/LIC_Manager.ui", self)
        self.closeBtn.clicked.connect(close_cliked)

        # Add Policy Tab
        self.addPolicyBtn.clicked.connect(self.add_policy)
        self.paidDateEdit.editingFinished.connect(self.due_date_change)
        self.nextPremiumDateEdit.setDate(datetime.datetime.today())

        # Search Policy Tab
        self.searchBtn.clicked.connect(self.search_policy)
        self.search_all.stateChanged.connect(self.state_changed)
        self.lb_update.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lb_InvalidSearch.hide()

        # Update Payment Tab
        self.de_paymentDt.setDate(datetime.datetime.today())
        self.btn_PaySearch.clicked.connect(self.pay_details)
        self.updateBtn.clicked.connect(self.update_payment)
        self.updateBtn.setEnabled(False)

        # Payment Due Tab
        self.getDueBtn.clicked.connect(self.get_payment_due)
        self.str_date = datetime.datetime.today().strftime('%d/%m/%Y')
        self.date_today.setText(str('Date: {}'.format(self.str_date)))
        self.dueTillDtBtn.setText(str('Get All Policies Due till Today : {}'.format(self.str_date)))
        self.dueTillDtBtn.clicked.connect(self.get_payment_due_till_dt)

        # Load All Policies
        self.policy_dict = {}
        self.policies_df = pd.DataFrame()
        self.policy_number_list = []
        self.load_policies()
        self.show()

    def get_all_policies_df(self):
        return self.policies_df

    def get_frequency(self, mode):
        frequency = {'Monthly': 1, 'Quarterly': 3, 'Half Yearly': 6, 'Yearly': 12}
        return frequency[mode] if mode in frequency else 0

    def load_policies(self):
        self.policies_df = pd.read_csv("../Data/polices.dat", sep='|')
        self.policy_number_list = self.policies_df['Number'].tolist()
        print(self.policy_number_list)
        print('Policies Loading Success')

    def due_date_change(self):
        cur_due_date = self.paidDateEdit.date().toPyDate()
        freq_text = self.freqComboBox.currentText()

        if freq_text in Frequency_dict:
            freq = int(Frequency_dict[self.freqComboBox.currentText()])
            print(freq)
            new_date = cur_due_date + relativedelta(months=freq)
            print(new_date)
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msgBox.setWindowTitle('Invalid Policy Mode')
            msgBox.setText('<b>Please enter valid policy mode / frequency </b>')
            msgBox.exec()

    def add_policy(self):
        print('add clicked')
        # print('Date : {}'.format(self.docDateEdit.date().toPyDate()))
        # print('term : {}'.format(self.termSpinBox.text()))

        dom = self.docDateEdit.date().toPyDate() + relativedelta(years=int(self.termSpinBox.text()))
        # print('dom : {}'.format(dom))

        freq = self.get_frequency(self.freqComboBox.currentText())
        nextPremDue = self.paidDateEdit.date().toPyDate() + relativedelta(months=freq)
        print('next premium date : {}'.format(nextPremDue))
        self.nextPremiumDateEdit.setDate(nextPremDue)

        number = self.numberLineEdit.text()
        self.policy_dict = {'Number': number, 'Name': self.nameComboBox.currentText(),
                            'DOC': self.docDateEdit.date().toPyDate(), 'SA': self.sumAssuredLineEdit.text(),
                            'Term': self.termSpinBox.text(), 'Mode': self.freqComboBox.currentText(),
                            'Premium': self.premiumLineEdit.text(), 'LastPrePayDate': self.paidDateEdit.date().toPyDate(),
                            'NextPrePayDueDt': nextPremDue, 'DOM': dom, 'LastPaymentDate': 'Not Available', 'Amount': self.premiumLineEdit.text()}

        if len(number) <= 0:
            print('Please enter policy Number')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setWindowTitle('Policy Number')
            msgBox.setText('<b>Please enter valid policy number.</b> <br><br> Correct policy number is required to add policy.')
            msgBox.exec()
            return

        if int(number) in self.policy_number_list:
            print('already available')
            msgBox1 = QtWidgets.QMessageBox()
            msgBox1.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox1.setWindowTitle('Policy Already Added')
            msgBox1.setText("<b>Please enter valid policy number.</b> <br><br> Already added policy cannot be add again.")
            msgBox1.exec()
            return
        else:
            print('policy not exist {}'.format(self.numberLineEdit.text().strip()))

        addObj = AddPolicy(self.policy_dict, self.policies_df)

        if addObj.get_status():
            msg_box_success = QtWidgets.QMessageBox()
            msg_box_success.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg_box_success.setWindowTitle('Add Policy')
            msg_box_success.setText('<b>Policy Added Successfully</b>.')
            msg_box_success.exec()
            self.load_policies()
        else:
            msg_box_failed = QtWidgets.QMessageBox()
            msg_box_failed.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg_box_failed.setWindowTitle('Add Policy')
            msg_box_failed.setText('<b>Failed to add policy.</b>.')
            msg_box_failed.exec()

    def state_changed(self):
        self.tw_policies.clearContents()
        self.tw_policies.setRowCount(0)
        if self.search_all.isChecked():
            self.le_policy.setEnabled(False)
        else:
            self.le_policy.setEnabled(True)

    def search_policy(self):
        is_all_search = False
        result_df = self.policies_df.copy(deep=True)
        if self.search_all.isChecked():
            print('Search all policies is enabled')
            self.le_policy.setEnabled(False)
            is_all_search = True
        else:
            is_all_search = False
            print('Search specific policies is enabled')
            self.le_policy.setEnabled(True)
            policy_number = str(self.le_policy.text()).strip()
            print('policy number {} - {}'.format(policy_number, type(policy_number)))
            df_search = self.policies_df.copy(deep=True)
            df_search['Number'] = df_search['Number'].astype("string")
            result_df = df_search.loc[df_search['Number'] == policy_number]

        result_df.reset_index(drop=True, inplace=True)

        if len(result_df) > 0:
            self.lb_InvalidSearch.hide()
            print(result_df.columns.values.tolist())
            print('searched result : {}'.format(result_df))

            self.tw_policies.setRowCount(len(result_df))
            self.tw_policies.setColumnCount(len(result_df.columns.values.tolist()))
            self.tw_policies.setHorizontalHeaderLabels(result_df.columns.values.tolist())
        else:
            self.lb_InvalidSearch.show()

        parent_items = []
        for index, row in result_df.iterrows():
            list_item = []

            item_number = QtWidgets.QTableWidgetItem(str(row['Number']))
            if not is_all_search:
                item_number.setToolTip(row['Number'])
            list_item.append(item_number)

            item_name = QtWidgets.QTableWidgetItem(row['Name'])
            if not is_all_search:
                item_name.setToolTip('Name: ' + row['Name'])
            list_item.append(item_name)

            item_doc = QtWidgets.QTableWidgetItem(row['DOC'])
            if not is_all_search:
                item_doc.setToolTip('Date of Commencement: ' + row['DOC'])
            list_item.append(item_doc)

            item_sa = QtWidgets.QTableWidgetItem(str(row['SA']))
            if not is_all_search:
                item_sa.setToolTip('Sum Assured: ' + str(row['SA']))
            list_item.append(item_sa)

            item_term = QtWidgets.QTableWidgetItem(str(row['Term']))
            if not is_all_search:
                item_term.setToolTip('Term: ' + str(row['Term']))
            list_item.append(item_term)

            item_freq = QtWidgets.QTableWidgetItem(row['Mode'])
            if not is_all_search:
                item_freq.setToolTip('Frequency: ' + row['Mode'])
            list_item.append(item_freq)

            item_premium = QtWidgets.QTableWidgetItem(str(row['Premium']))
            if not is_all_search:
                item_premium.setToolTip('Premium Amount: ' + str(row['Premium']))
            list_item.append(item_premium)

            item_prem_dt = QtWidgets.QTableWidgetItem(row['LastPrePayDate'])
            if not is_all_search:
                item_prem_dt.setToolTip('Last Premium Paid / Due Date: ' + row['LastPrePayDate'])
            list_item.append(item_prem_dt)

            item_pay_dt = QtWidgets.QTableWidgetItem(row['NextPrePayDueDt'])
            if not is_all_search:
                item_pay_dt.setToolTip('Next Premium Due Date: ' + row['NextPrePayDueDt'])
            list_item.append(item_pay_dt)

            item_dom = QtWidgets.QTableWidgetItem(row['DOM'])
            if not is_all_search:
                item_dom.setToolTip('Date of Maturity: ' + row['DOM'])
            list_item.append(item_dom)

            item_lstpaydt = QtWidgets.QTableWidgetItem(str(row['LastPaymentDate']))
            if not is_all_search:
                item_lstpaydt.setToolTip('Last Payment Date: ' + str(row['LastPaymentDate']))
            list_item.append(item_lstpaydt)

            item_amt = QtWidgets.QTableWidgetItem(str(row['Amount']))
            if not is_all_search:
                item_amt.setToolTip('Amount:' + str(row['Amount']))
            list_item.append(item_amt)

            parent_items.append(list_item)
            # print('appended successfully row for index : {}'.format(index))
            # item_index = 0
            # for item in list_item:
            #     item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            #     item.setBackground(QtGui.QColor(255, 255, 255))
            #     self.tw_policies.setItem(index, item_index, item)
            #     item_index += 1

        index = 0
        for list_item in parent_items:
            item_index = 0
            for item in list_item:
                # print('item : {}'.format(item))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QtGui.QColor(255, 255, 255))
                self.tw_policies.setItem(index, item_index, item)
                item_index += 1
            index += 1

        self.tw_policies.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tw_policies.show()

    def pay_details(self):
        policy_number = str(self.le_pay_policy_search.text()).strip()
        df_search = self.policies_df.copy(deep=True)
        df_search['Number'] = df_search['Number'].astype("string")
        result_df = df_search.loc[df_search['Number'] == policy_number]
        result_df.reset_index(drop=True, inplace=True)
        print(result_df)
        if len(result_df) > 0:
            self.updateBtn.setEnabled(True)
            self.le_holderName.setText(result_df['Name'][0])
            self.le_holderName.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            self.le_premiumAmt.setText(str(result_df['Premium'][0]))
            self.le_premiumAmt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            self.le_dueDate.setText(str(result_df['NextPrePayDueDt'][0]))
            self.le_dueDate.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            self.le_lastPayDate.setText(str(result_df['LastPaymentDate'][0]))
            self.le_lastPayDate.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            freq = self.get_frequency(str(result_df['Mode'][0]))
            print(str(result_df['NextPrePayDueDt'][0]).strip(), type(result_df['NextPrePayDueDt'][0]))
            date_obj = pd.to_datetime(result_df['NextPrePayDueDt'][0]).date() + relativedelta(months=freq)
            next_payment_due = date_obj.strftime('%Y-%m-%d')
            self.le_futureDtOnUpdate.setText(next_payment_due)
        else:
            self.updateBtn.setEnabled(False)
            print('Update Payment')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setWindowTitle('Invalid Policy Number')
            msgBox.setText('<b>Please enter valid policy number.</b> <br><br> Policy number is not found to update policy payment details.')
            msgBox.exec()

    def update_payment(self):
        df_update_payment = self.get_all_policies_df().copy(deep=True)

        # Force 'Number' column to string for accurate matching
        df_update_payment['Number'] = df_update_payment['Number'].astype(str)

        policy_number = str(self.le_pay_policy_search.text()).strip()
        payment_date = self.de_paymentDt.date().toPyDate()
        dt = datetime.date(2020, 1, 1)
        payment_amt = self.le_paidAmount.text()

        due_date_str = self.le_dueDate.text().strip()
        due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d')
        min_pay_date = due_date - relativedelta(months=1)
        print(min_pay_date)

        if min_pay_date.date() > datetime.date.today():
            msg_box_critical = QtWidgets.QMessageBox()
            msg_box_critical.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg_box_critical.setWindowTitle('LIC of India - Future Due Policy')
            msg_box_critical.setText('<b>As per LIC of India future due premium is not allowed to pay before one month'
                                     ' from due date.</b><br><br> Pay premium after <b> {} </b> and then update'
                                     .format(min_pay_date.strftime('%d/%m/%Y')))
            msg_box_critical.exec()
            return
        else:
            print(' Allowed payment date is on or after {}'.format(min_pay_date))

        print('Updating....**')
        if payment_date > dt and len(payment_amt) > 0:
            mask = df_update_payment['Number'] == policy_number
            if mask.any():
                nextPrePayDueDt = self.le_futureDtOnUpdate.text().strip()
                lastPrePayDate = self.le_dueDate.text().strip()

                df_update_payment.loc[mask, 'LastPrePayDate'] = lastPrePayDate
                df_update_payment.loc[mask, 'NextPrePayDueDt'] = nextPrePayDueDt
                df_update_payment.loc[mask, 'LastPaymentDate'] = str(payment_date)
                df_update_payment.loc[mask, 'Amount'] = float(payment_amt)

                print("Updated Row:")
                print(df_update_payment.loc[mask])

                df_update_payment.to_csv("../Data/polices.dat", sep='|', index=False)
                self.load_policies()
                print("Updated successfully.")
            else:
                print(f"No matching policy number found: {policy_number}")
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setWindowTitle('Invalid Payment Date or Amount')
            msgBox.setText('<b>Please enter valid Payment Date and Amount .</b> <br><br> Payment date should be after 01/01/2020. <br> Amount should be greater than 0')
            msgBox.exec()

    def populate_tw_payment_due(self, rslt_df):
        print(rslt_df)
        if len(rslt_df) > 0:
            print(rslt_df.columns.values.tolist())
            print('searched result : {}'.format(rslt_df))

            self.tw_payment_due.setRowCount(len(rslt_df))
            self.tw_payment_due.setColumnCount(len(rslt_df.columns.values.tolist()))
            self.tw_payment_due.setHorizontalHeaderLabels(rslt_df.columns.values.tolist())
            self.tw_payment_due.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            parent_items = []
            for index, row in rslt_df.iterrows():
                print(row)
                next_prem_due_dt = str(str(row['NextPrePayDueDt']).split(" ")[0])
                list_item = []

                items_number = QtWidgets.QTableWidgetItem(str(row['Number']))
                list_item.append(items_number)

                items_name = QtWidgets.QTableWidgetItem(row['Name'])
                list_item.append(items_name)

                items_doc = QtWidgets.QTableWidgetItem(row['DOC'])
                list_item.append(items_doc)

                items_sa = QtWidgets.QTableWidgetItem(str(row['SA']))
                list_item.append(items_sa)

                items_term = QtWidgets.QTableWidgetItem(str(row['Term']))
                list_item.append(items_term)

                items_freq = QtWidgets.QTableWidgetItem(row['Mode'])
                list_item.append(items_freq)

                items_premium = QtWidgets.QTableWidgetItem(str(row['Premium']))
                list_item.append(items_premium)

                items_prem_dt = QtWidgets.QTableWidgetItem(row['LastPrePayDate'])
                list_item.append(items_prem_dt)

                items_pay_dt = QtWidgets.QTableWidgetItem(next_prem_due_dt)
                list_item.append(items_pay_dt)

                items_dom = QtWidgets.QTableWidgetItem(row['DOM'])
                list_item.append(items_dom)

                items_lstpaydt = QtWidgets.QTableWidgetItem(str(row['LastPaymentDate']))
                list_item.append(items_lstpaydt)

                items_amt = QtWidgets.QTableWidgetItem(str(row['Amount']))
                list_item.append(items_amt)

                parent_items.append(list_item)

            indexs = 0
            for list_item in parent_items:
                items_index = 0
                for items in list_item:
                    # print('item : {}'.format(item))
                    items.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    items.setBackground(QtGui.QColor(255, 255, 255))
                    self.tw_payment_due.setItem(indexs, items_index, items)
                    items_index += 1
                indexs += 1

            self.tw_payment_due.show()

        else:
            msg_box_success = QtWidgets.QMessageBox()
            msg_box_success.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg_box_success.setWindowTitle('Due For Payment')
            msg_box_success.setText('<b> No policy is due for payment. </b>')
            msg_box_success.exec()

    def get_payment_due(self):
        self.tw_payment_due.clearContents()
        df_policies = self.policies_df.copy(deep=True)
        print('get payment dues {}'.format(self.str_date))
        isThirtyDays = self.rb_thirtydays.isChecked()
        isNintyDays = self.rb_nintydays.isChecked()
        isSixMonths = self.rb_sixmonths.isChecked()
        isOneYear = self.rb_oneyear.isChecked()
        today = datetime.date.today()
        nextDate = None

        if isThirtyDays:
            nextDate = today + relativedelta(months=+1)
            print(nextDate)
        elif isNintyDays:
            nextDate = today + relativedelta(months=+3)
            print(nextDate)
        elif isSixMonths:
            nextDate = today + relativedelta(months=+6)
            print(nextDate)
        elif isOneYear:
            nextDate = today + relativedelta(months=+12)
            print(nextDate)
        else:
            print('not selected')

        # Make sure 'NextPrePayDueDt' is datetime64
        df_policies['NextPrePayDueDt'] = pd.to_datetime(df_policies['NextPrePayDueDt'])

        # Generate date range from today to nextDate (as Timestamps)
        date_range = pd.date_range(start=today, end=nextDate)

        # Filter rows where 'NextPrePayDueDt' falls within the range
        rslt_df = df_policies[df_policies['NextPrePayDueDt'].isin(date_range)]
        self.populate_tw_payment_due(rslt_df)

        # nextDate = nextDate.strftime('%Y-%m-%d')
        # today = today.strftime('%Y-%m-%d')
        #
        # df_policies['NextPrePayDueDt'] = df_policies['NextPrePayDueDt'].astype('datetime64[ns]')
        # rslt_df = df_policies[df_policies['NextPrePayDueDt'].isin(pd.date_range(today, nextDate))]

    def get_payment_due_till_dt(self):
        print('show policies duw till date')
        self.tw_payment_due.clearContents()
        df_policies = self.policies_df.copy(deep=True)
        today = datetime.date.today().strftime('%Y-%m-%d')

        df_policies['NextPrePayDueDt'] = pd.to_datetime(df_policies['NextPrePayDueDt'])
        # Filter rows where date is less than today
        due_policies_df = df_policies[df_policies['NextPrePayDueDt'] < pd.Timestamp(today)]

        self.populate_tw_payment_due(due_policies_df)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = Main()
    sys.exit(app.exec())
