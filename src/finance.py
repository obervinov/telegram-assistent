# THIS FILE IS NEEDED TO PROCESS INCOMING EXPENSE DATA AND CALCULATE THE REPORT #

# Importing modules #
import re
from datetime import date, datetime
from logger import log


class AssistentFinance:

    def __init__(self, vault=None, bot_name: str = None):
        # Variables #
        self.vault = vault
        self.bot_name = bot_name


    # Adding new financial item in storage
    def finance_add_items(self, message, type: str = None):
        try:
            timestamp = date.today().strftime('%Y-%m')
            data = message.text.split("\n")

            for item in data:
                key = re.search("\D+", item).group()[:-1]
                value = re.search("\d+", item).group()
                exist_values = self.vault.vault_read_secrets(f"{self.bot_name}-data/{type}/{timestamp}")

                # We check whether the key already exists in the bucket,
                # if it exists, we summarize the values,
                # if not, we write it as is
                if key in exist_values:
                    log.info(
                      f"AssistentFinance.finance_add_items(): "
                      f"the key '{key}' already exists, "
                      f"summation of values"
                      )
                    exist_value = exist_values[key]
                    exist_value = int(exist_value)
                    cost = int(exist_value) + int(value)
                    self.vault.vault_put_secrets(f"{self.bot_name}-data/{type}/{timestamp}", key, cost)

                elif key not in exist_values:
                    log.info(
                      f"AssistentFinance.finance_add_items(): "
                      f"the key '{key}' doesn't exists, "
                      f"creating key"
                      )
                    self.vault.vault_put_secrets(f"{self.bot_name}-data/{type}/{timestamp}", key, value)

                else:
                    log.error(
                      f"AssistentFinance.finance_add_items(): "
                      f"exception during key '{key}' processing"
                      )

        except Exception as ex:
            log.error(f"AssistentFinance.finance_add_items(): exception: {ex}")


    # Creating financial report by month
    def finance_get_report(self, month: str = None):
        month_num = datetime.strptime(month, '%b').month
        year = date.today().strftime('%Y')

        # We read from the vault the entire timestamp associated with income and expenses
        log.info(
          f"AssistentFinance.finance_get_report(): "
          f"reading expenses and receipts "
          f"by {year}-{month_num}"
          )
        expenses_data = self.vault.vault_read_secrets(f"{self.bot_name}-data/expenses/{year}-{month_num}")
        receipts_data = self.vault.vault_read_secrets(f"{self.bot_name}-data/receipts/{year}-{month_num}")

        # We subtract the lists of categories (to group expenses by category)
        log.info(
          f"AssistentFinance.finance_get_report(): "
          f"reading categories "
          f"by {self.bot_name}-data/categories"
          )
        category_food = self.vault.vault_read_secrets(
                                      f"{self.bot_name}-data/categories",
                                      "food"
                                      )
        category_compulsory = self.vault.vault_read_secrets(
                                      f"{self.bot_name}-data/categories",
                                      "mandatory payments"
                                      )
        category_cat = self.vault.vault_read_secrets(
                                      f"{self.bot_name}-data/categories",
                                      "cat"
                                      )

        # We start the dictionaries and counters necessary for calculations
        raw_data_expenses = {}
        raw_data_receipts = {}
        receipts_dict = {}
        receipts_total = 0
        compulsory_expenses_dict = {}
        compulsory_expenses_total = 0
        food_expenses_dict = {}
        food_expenses_total = 0
        cat_expenses_dict = {}
        cat_expenses_total = 0
        additional_expenses_dict = {}
        additional_expenses_total = 0

        # We parse the date by expenses -
        # we collect dictionaries of categories with positions and calculate the amount of expenses
        log.info(
          "AssistentFinance.finance_get_report(): "
          "building a dictionary expenses by categories"
          )
        if "InvalidPath" not in expenses_data.values():
            for item in expenses_data:
                # For the food/groceries category
                if item in category_food:
                    food_expenses_dict.update({item: int(expenses_data[item])})
                    food_expenses_total = food_expenses_total + int(expenses_data[item])
                # For the category of mandatory payments
                elif item in category_compulsory:
                    compulsory_expenses_dict.update({item: int(expenses_data[item])})
                    compulsory_expenses_total = compulsory_expenses_total + int(expenses_data[item])
                # For the category of car expenses
                elif item in category_cat:
                    cat_expenses_dict.update({item: int(expenses_data[item])})
                    cat_expenses_total = cat_expenses_total + int(expenses_data[item])
                # All other expenses in the category of additional expenses
                else:
                    additional_expenses_dict.update({item: int(expenses_data[item])})
                    additional_expenses_total = additional_expenses_total + int(expenses_data[item])

        # We parse the date by income - we collect a dictionary with the amount and a list
        log.info(
          "AssistentFinance.finance_get_report(): "
          "building a dictionary income"
          )
        if "InvalidPath" not in receipts_data.values():
            for item in receipts_data.items():
                receipts_dict.update({item[0]: int(item[1])})
                receipts_total = receipts_total + int(item[1])

        # We collect the final dictionaries with the necessary categories,
        # which will be passed to generate the html body of the message with the report
        raw_data_receipts.update(
          {'Income': {'total': receipts_total, 'items': receipts_dict}}
          )
        raw_data_expenses.update(
          {'Food': {'total': food_expenses_total, 'items': food_expenses_dict}}
          )
        raw_data_expenses.update(
          {'Monthly payments': {'total': compulsory_expenses_total, 'items': compulsory_expenses_dict}}
          )
        raw_data_expenses.update(
          {'Cat expenses': {'total': cat_expenses_total, 'items': cat_expenses_dict}}
          )
        raw_data_expenses.update(
          {'Additional expenses': {'total': additional_expenses_total, 'items': additional_expenses_dict}}
          )

        return f"{year}-{month_num}", raw_data_expenses, raw_data_receipts
