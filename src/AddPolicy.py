import pandas as pd
from tabulate import tabulate


class AddPolicy:
    def __init__(self, policy_dict, all_policies_df):
        print('inside class ... all policies :')
        print(all_policies_df)
        print(all_policies_df.columns)
        print('Add Policy Called...  ' + str(policy_dict) + ".")
        polices_df = pd.DataFrame([policy_dict])
        print(polices_df)
        print(polices_df.columns)
        print('============== Before addition =====================')
        self.status = False
        try:
            all_policies_df = pd.concat([all_policies_df, polices_df], axis=0)
            print('==============After addition =====================')
            print(tabulate(all_policies_df))
            all_policies_df.to_csv("../Data/polices.dat", sep='|', index=False)
            self.status = True
        except e:
            print('error : {}'.format(e))

    def get_status(self):
        print('get status called : {}'.format(self.status))
        return self.status




# self.tw_policies.setItem(index, 0, item_number)
# self.tw_policies.setItem(index, 1, item_name)
# self.tw_policies.setItem(index, 2, item_doc)
# self.tw_policies.setItem(index, 3, item_sa)
# self.tw_policies.setItem(index, 4, item_term)
# self.tw_policies.setItem(index, 5, item_freq)
# self.tw_policies.setItem(index, 6, item_premium)
# self.tw_policies.setItem(index, 7, item_dom)
# self.tw_policies.setItem(index, 8, item_prem_dt)


# self.tw_policies.resizeColumnsToContents()
# # self.tw_policies.resizeRowsToContents()
# self.tw_policies.horizontalHeader().setStretchLastSection(True)
