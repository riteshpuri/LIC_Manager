import os
import sys
import pandas as pd
import datetime as datetime
from tabulate import tabulate
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from dateutil.relativedelta import relativedelta
from InsuranceManager.src.AddPolicy import AddPolicy


LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))

Frequency_dict = {'Monthly': 1, 'Quarterly': 3, 'Half Yearly': 6, 'Yearly': 12}


def close_cliked():
    print('Exiting')
    exit(0)

class Main(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(LOCAL_DIR + "/LIC_Manager.ui", self)
        self.closeBtn.clicked.connect(close_cliked)

        # Add Policy Tab
        self.addPolicyBtn.clicked.connect(self.add_policy)
        self.paidDateEdit.editingFinished.connect(self.due_date_change)

        # Search Policy Tab
        self.searchBtn.clicked.connect(self.search_policy)
        self.search_all.stateChanged.connect(self.state_changed)
        self.lb_update.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lb_InvalidSearch.hide()

        # Update Payment Tab
        self.btn_PaySearch.clicked.connect(self.pay_details)
        self.updateBtn.clicked.connect(self.update_payment)
        self.updateBtn.setEnabled(False)

        # Payment Due Tab
        self.getDueBtn.clicked.connect(self.get_payment_due)
        str_date = datetime.datetime.today().strftime('%d/%m/%Y')
        self.date_today.setText(str('Date: {}'.format(str_date)))
        self.dueTillDtBtn.setText(str('Get All Policies Due till Today : {}'.format(str_date)))

        # Load All Policies
        self.policy_dict = {}
        self.policies_df = self.load_policies()
        # print(tabulate(self.policies_df))
        self.show()

    def get_frequency(self, mode):
        frequency = {'Monthly': 1, 'Quarterly': 3, 'Half Yearly': 6, 'Yearly': 12}
        return frequency[mode] if mode in frequency else 0

    def load_policies(self):
        return pd.read_csv("../Data/polices.dat", sep='|')

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
        print('Date : {}'.format(self.docDateEdit.date().toPyDate()))
        print('term : {}'.format(self.termSpinBox.text()))

        dom = self.docDateEdit.date().toPyDate() + relativedelta(years=int(self.termSpinBox.text()))
        print('dom : {}'.format(dom))

        freq = self.get_frequency(self.freqComboBox.currentText())
        nextPremDue = self.paidDateEdit.date().toPyDate() + relativedelta(months=freq)
        self.nextPremiumDateEdit.setDate(nextPremDue)

        self.policy_dict = {'Number': self.numberLineEdit.text(), 'Name': self.nameComboBox.currentText(),
                            'DOC': self.docDateEdit.date().toPyDate(), 'SA': self.sumAssuredLineEdit.text(),
                            'Term': self.termSpinBox.text(), 'Mode': self.freqComboBox.currentText(),
                            'Premium': self.premiumLineEdit.text(), 'LastPrePayDate': self.paidDateEdit.date().toPyDate(),
                            'NextPrePayDueDt': nextPremDue, 'DOM': dom, 'LastPaymentDate': 'Not Available', 'Amount': self.premiumLineEdit.text()}

        if len(self.numberLineEdit.text().strip()) <= 0:
            print('Please enter policy Number')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msgBox.setWindowTitle('Policy Number')
            msgBox.setText('<b>Please enter valid policy number.</b> <br><br> Correct Policy number is required to add policy details.')
            msgBox.exec()

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
            msg_box_failed.setIcon(QtWidgets.QMessageBox.Icon.Error)
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
        result_df = self.policies_df
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
            df_search = self.policies_df
            df_search['Number'] = df_search['Number'].astype("string")
            result_df = df_search.loc[df_search['Number'] == policy_number]

        result_df.reset_index(drop=True, inplace=True)

        if len(result_df) > 0:
            self.lb_InvalidSearch.hide()
            # print('===========================================================')
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

        self.tw_policies.show()

    def pay_details(self):
        policy_number = str(self.le_pay_policy_search.text()).strip()
        df_search = self.policies_df
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
        policy_number = str(self.le_pay_policy_search.text()).strip()
        payment_date = self.de_paymentDt.date().toPyDate()
        dt = datetime.date(2020, 1, 1)
        print('Updating....')
        payment_amt = self.le_paidAmount.text()
        if payment_date > dt and len(payment_amt) > 0:
            nextPrePayDueDt = self.le_futureDtOnUpdate.text()
            lastPrePayDate = self.le_dueDate.text()
            self.policies_df.loc[self.policies_df['Number'] == policy_number, 'LastPrePayDate'] = lastPrePayDate
            self.policies_df.loc[self.policies_df['Number'] == policy_number, 'NextPrePayDueDt'] = nextPrePayDueDt
            self.policies_df.loc[self.policies_df['Number'] == policy_number, 'LastPaymentDate'] = payment_date
            self.policies_df.loc[self.policies_df['Number'] == policy_number, 'Amount'] = str(payment_amt)
            print('Updated successfully')
            self.policies_df.to_csv("../Data/polices.dat", sep='|', index=False)
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msgBox.setWindowTitle('Invalid Payment Date or Amount')
            msgBox.setText('<b>Please enter valid Payment Date and Amount .</b> <br><br> Payment date should be after 01/01/2020. <br> Amount should be greater than 0')
            msgBox.exec()

    def get_payment_due(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = Main()
    sys.exit(app.exec())
