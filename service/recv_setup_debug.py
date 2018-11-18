import config
import recv_setup
import recv_db

def list_all_accounts():
    accounts = recv_db.get_all_accounts()
    print("Listing all receiver accounts", len(accounts))
    for a in accounts:
        print(a['rec_acc'], a['pool_account_id'], a['user_data'], a['create_root_acc'], a['acc_idx'], a['create_wallet_id'], a['created_time'], a['status'], a['updated_time'])

config = config.readConfig()
recv_setup.setup_check()
#list_all_accounts()
