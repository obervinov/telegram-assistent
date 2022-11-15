# THIS FILE WITH RESPONSE BODY TEMPLATES #

class MessageBody:

    def __init__(self) -> None:
        # Text #
        self.bot_startup_message = "Hi, <b>{0}</b> {1}\n<b>What I can do:</b> {2}\n    {3}"
        self.bot_functions_list = [
            'Recording of financial expenses',
            'Recording of financial income',
            "Generate a monthly financial report"
            ]
        self.buttons_finance = [
            "Adding Expenses",
            "Adding Income",
            "Getting Report"
            ]
        self.help_finance_expenses = (
            "To account for <b>expenses</b>, "
            "enter expenses as a list.\n"
            "<b>Example:</b>\n<code>supermarket 500\ntaxi 250</code>"
            )
        self.help_finance_income = (
            "To account for <b>income</b>, "
            "specify the period and positions in the list.\n"
            "<b>Example:</b>\n<code>payday 200000</code>"
            )
        self.help_finance_report = (
            "{emoji} Select month for the creating report"
            )
        self.buttons_finance_report = [
            'Jan', 'Feb', 'Mar', 'Apr',
            'May', 'June', 'July', 'Aug',
            'Sept', 'Oct', 'Nov', 'Dec'
            ]
        self.expenses_finance_report = (
            "{expenses} - "
            "{item}\n"
            )
        self.body_expenses_finance_report = (
            "{emoji} <b>{category}:</b>\n"
            "{expenses_list}"
            "<b>Total: {expenses_total_by_category}</b>\n\n"
            )
        self.income_finance_report = (
            "{receipts} - "
            "{item}\n"
            )
        self.body_income_finance_report = (
            "{emoji} <b>Income:</b>\n"
            "{receipts_list}"
            "<b>Total: {receipts_total}</b>\n\n"
            )
        self.body_summary_finance_report = (
            "{emoji} <b>Total summary:</b>\n"
            "Total expenses: {expenses_total}\n"
            "Balance at the end of the month: {balance}\n\n"
            )
        self.body_finance_report = (
            "{emoji} Financial report for <b>{date}</b>:\n\n"
            "{report_body_receipts_category}-----\n\n"
            "{report_body_expenses_category}-----\n\n"
            "{report_body_summary}"
            )

        # Emoji codes #
        self.bot_emoji_hi = "\U0001F44B"
        self.bot_emoji_info = "\U0001F4CC"
        self.bot_emoji_list = "\U0001F4CD"
        self.emoji_receipts = "\U0001F4B8"
        self.emoji_report = "\U0001F4C5"
        self.emoji_police = "\U0001F6A8"
        self.emoji_food = "\U0001F354"
        self.emoji_additional = "\U0001F37A"
        self.emoji_summary = "\U0001F4C4"
        self.emoji_car = "\U0001F697"
        self.emoji_cat = "\U0001F408"
        self.emoji_calender = "\U0001F4C5"

    # Building message #
    def build_message_response(self, type: str = None, **kwargs):
        # Buil startup message
        if type == "bot_startup_message":
            message = kwargs.get('message')
            functions_list = str()
            for item in self.bot_functions_list:
                functions_list = self.bot_emoji_list + item + "\n    " + functions_list
            response = self.bot_startup_message.format(
                                message.chat.username,
                                self.bot_emoji_hi,
                                self.bot_emoji_info,
                                functions_list
                                )

        elif type == "buttons_finance":
            response = self.buttons_finance

        elif type == "help_finance_expenses":
            response = self.help_finance_expenses

        elif type == "help_finance_income":
            response = self.help_finance_income

        elif type == "help_finance_report":
            response = self.help_finance_report.format(
                                emoji=self.emoji_calender
                                )

        elif type == "buttons_finance_report":
            response = self.buttons_finance_report

        elif type == "report_body":
            # Exctracting arguments
            raw_data_expenses = kwargs.get('raw_data_expenses')
            raw_data_receipts = kwargs.get('raw_data_receipts')
            date = kwargs.get('date')

            # Generating report html-body with receipts
            receipts_total = raw_data_receipts.get('Income').get('total')
            receipts_items = raw_data_receipts.get('Income').get('items')
            receipts_list = ""
            for item in receipts_items.items():
                receipts_list = receipts_list + self.income_finance_report.format(
                    receipts=item[1],
                    item=item[0]
                    )

            report_body_receipts_category = self.body_income_finance_report.format(
                emoji=self.emoji_receipts,
                receipts_list=receipts_list,
                receipts_total=receipts_total
                )

            # Generating report html-body with expenses
            report_body_expenses_category = ""
            report_body_expenses_total = 0
            # Getting all category names from a dict
            for category in raw_data_expenses.keys():
                expenses_list = ""
                # Getting dict with expense items
                expenses_items = raw_data_expenses.get(category).get('items')

                # Extracting key and value by expense item
                for item in expenses_items.items():
                    # Building html body with list
                    expenses_list = expenses_list + self.expenses_finance_report.format(
                        expenses=item[1],
                        item=item[0]
                        )

                # Getting dict with expense total
                expenses_total_by_category = raw_data_expenses.get(category).get('total')
                # Summary expensies total
                report_body_expenses_total = report_body_expenses_total + expenses_total_by_category

                # Selecting emoji for category
                if "Food" in category:
                    emoji = self.emoji_food
                elif "Monthly payments" in category:
                    emoji = self.emoji_police
                elif "Additional expenses" in category:
                    emoji = self.emoji_additional
                elif "Cat expenses" in category:
                    emoji = self.emoji_cat

                # Getting dict with expense categories
                report_body_expenses_category = report_body_expenses_category + self.body_expenses_finance_report.format(
                    emoji=emoji,
                    category=category,
                    expenses_list=expenses_list,
                    expenses_total_by_category=expenses_total_by_category
                    )

            report_body_summary = self.body_summary_finance_report.format(
                emoji=self.emoji_summary,
                expenses_total=report_body_expenses_total,
                receipts_total=receipts_total,
                balance=receipts_total-report_body_expenses_total
                )
            response = self.body_finance_report.format(
                emoji=self.emoji_report,
                date=date,
                report_body_receipts_category=report_body_receipts_category,
                report_body_expenses_category=report_body_expenses_category,
                report_body_summary=report_body_summary
                )

        return response
