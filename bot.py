# THIS MAIN FUNCTION FROM TELEGRAM BOT AND ENTRYPOINT FROM DOCKER #

# Importing modules #
import os
from logger import log, logging
from vault import VaultClient
from users import UsersAuth
from telegram import TelegramBot
from src.messages import MessageBody
from src.finance import AssistentFinance

# Environment variables #
bot_name = os.environ.get('BOT_NAME', 'telegram-assistent')
vault_mount_point = os.environ.get('BOT_VAULT_MOUNT_PATH', 'secretv2')
vault_addr = os.environ.get('BOT_VAULT_ADDR', 'http://vault-server:8200')
vault_approle_id = os.environ.get('BOT_VAULT_APPROLE_ID', 'not set')
vault_approle_secret_id = os.environ.get('BOT_VAULT_APPROLE_SECRET_ID', 'not set')

# Initing vault class #
vault = VaultClient(vault_addr, vault_approle_id, vault_approle_secret_id, vault_mount_point)

# Initing telebot class #
telegram = TelegramBot(bot_name, vault)
telegram_bot = telegram.telegram_bot
telegram_types = telegram.telegram_types

# Initing users class #
users_auth = UsersAuth(vault, bot_name)

# Initiing messages class #
messages = MessageBody()

# Initing finance class #
finance = AssistentFinance(vault, bot_name)


# Decorators #
# Start command
@telegram_bot.message_handler(commands=['start'])
def telebot_startup(message):
    # Check permissions
    access_status = users_auth.check_permission(message.chat.id)
    if access_status == "success":
        # Creating markup for buttons
        markup = telegram_types.InlineKeyboardMarkup()
        functions = messages.build_message_response(
                            "buttons_finance"
                            )
        # Creating a button object by listß
        buttons = []
        for function in functions:
            buttons.append(
                telegram_types.InlineKeyboardButton(
                    function,
                    callback_data=function
                    )
                )
        # Splitting buttons list to matrix 2x2
        size = 2
        for x in range(0, len(buttons), size):
            markup.row(*buttons[x:x+size])
        # Send reply with buttons
        telegram_bot.reply_to(
            message,
            messages.build_message_response(
                        'bot_startup_message',
                        message=message
                        ),
            reply_markup=markup
            )
        log.info(f"sending startup message in chat {message.chat.id}")
    else:
        log.error(f"403: Forbidden for username: {message.from_user.username}")


# Callback query handler for InlineKeyboardButton
@telegram_bot.callback_query_handler(func=lambda call: True)
def telebot_callback_query_handler(call):
    # Check permissions
    access_status = users_auth.check_permission(call.message.chat.id)
    if access_status == "success":

        # Select routes
        # For Adding Expenses
        if call.data == "Adding Expenses":
            help_message = telegram_bot.send_message(
                                call.message.chat.id,
                                messages.build_message_response(
                                    "help_finance_expenses"
                                    )
                                )
            telegram_bot.register_next_step_handler(
                call.message,
                telebot_added_expense_handling,
                help_message
                )

        # For Adding Income
        elif call.data == "Adding Income":
            help_message = telegram_bot.send_message(
                                call.message.chat.id,
                                messages.build_message_response(
                                    "help_finance_income"
                                    )
                                )
            telegram_bot.register_next_step_handler(
                call.message,
                telebot_added_income_handling,
                help_message
                )

        # For Getting Report
        elif call.data == "Getting Report":
            # Creating markup for buttons
            markup = telegram_types.InlineKeyboardMarkup()
            months = messages.build_message_response(
                                "buttons_finance_report"
                                )
            # Creating a button object by list
            buttons = []
            for month in months:
                buttons.append(
                    telegram_types.InlineKeyboardButton(
                        month,
                        callback_data=month
                    )
                )
            # Splitting buttons list to matrix 4x3
            size = 4
            for x in range(0, len(buttons), size):
                markup.row(*buttons[x:x+size])
            # Send reply with buttons
            telegram_bot.send_message(
                call.message.chat.id,
                messages.build_message_response(
                    'help_finance_report'
                    ),
                reply_markup=markup
                )

        # For Report by Month
        elif call.data in messages.build_message_response(
                                "buttons_finance_report"
                                ):
            log.info(
                f"Decorator.calender_callback_query() --> "
                f"call Finance.finance_get_report() "
                f"by chat_id {call.message.chat.id}"
                )
            date, raw_data_expenses, raw_data_receipts = finance.finance_get_report(
                call.data
            )
            telegram_bot.send_message(
                call.message.chat.id,
                messages.build_message_response(
                    "report_body",
                    raw_data_expenses=raw_data_expenses,
                    raw_data_receipts=raw_data_receipts,
                    date=date
                    )
                )
    else:
        log.error(f"403: Forbidden for username: {call.from_user.username}")


# Add financial expenses
def telebot_added_expense_handling(message, help_message):
    log.info(
        f"Decorator.telebot_added_expense_handling() --> "
        f"call Finance.finance_add_items() "
        f"by chat_id {message.chat.id}"
        )
    finance.finance_add_items(
        message,
        "expenses"
        )
    # Clearing trash message
    telegram_bot.delete_message(
        message.chat.id,
        help_message.id
        )


# Add financial income
def telebot_added_income_handling(message, help_message):
    logging.info(
        f"Decorator.telebot_added_income_handling() --> "
        f"call Finance.finance_add_items() "
        f"by chat_id {message.chat.id}"
        )
    finance.finance_add_items(
        message,
        "receipts"
        )
    # Clearing trash message
    telegram_bot.delete_message(
        message.chat.id,
        help_message.id
        )


# Starting bot #
def main():
    while True:
        try:
            log.info(f"Starting telegram bot: {bot_name}")
            log.info(f"Home path: {os.getcwd()}")
            log.info(f"Vault: {vault_addr}")
            telegram_bot.polling()
        except Exception as ex:
            log.error(f"Strating telegram bot exception: {ex}")


if __name__ == "__main__":
    main()
