#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import re
import traceback
from datetime import timedelta
from io import BytesIO, StringIO
from os import linesep

import requests

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
from lib.exception import PdfParseError
from lib.utils import is_group_name
from service.schedule_cashe_service import schedule_cache, pdf_parser, pdf_list_cache, POWER_CUT_PAGE_KEY, \
    schedule_planner


def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Use /schedule <Group letter> <YYYY-MM-DD> to check schedule')


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    update.message.reply_text('Sorry, something went wrong')


def show_schedule(update: Update, context: CallbackContext) -> None:
    logging.info('--> Requested schedule with args %s by chat_id %s', context.args, update.message.chat_id)
    pdf_list = pdf_list_cache.get(POWER_CUT_PAGE_KEY)
    # ?????? ?????????????????? ?????????? ?????????????????? ????????, ?????? ?????? pdf_list - ?????? ?????????????????????????? dict
    dt, pdf_link = next(iter(pdf_list.items()))

    if len(context.args) > 1:
        date_candidate = context.args[1]
        # TODO ???????????????? ?????????????????? ?????????????? ????????, ???????? ???????????? ???????????????? - ???????????????? ???? ????????
        if date_candidate in pdf_list:
            logging.info('Choosing date from message...')
            dt = date_candidate
            pdf_link = pdf_list[dt]
        else:
            logging.info('Rejecting wrong date...')
            update.message.reply_text(f'Sorry, schedule for date "{date_candidate}" is not available.')
            return
    logging.info('Selected %s, %s', dt, pdf_link)
    try:
        groups, periods = schedule_cache.get((dt, pdf_link))
    except PdfParseError:
        update.message.reply_markdown(f'Parsing pdf file failed, but you can see it [here]({pdf_link}) manually.')
        return
    group_name = context.args[0].upper()
    if not is_group_name(group_name):
        update.message.reply_text('Please select a proper group using one letter')
        return

    schedule = schedule_planner.get_schedule(groups, periods, group_name)
    schedule_message = schedule_planner.get_schedule_message(schedule, pdf_link, dt, group_name)
    logging.info('<-- Schedule for %s in %s is %s', dt, group_name, schedule)
    update.message.reply_markdown(schedule_message)


def get_schedule_updates(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    group_name = job.context['group_name']
    context.bot.send_message(job.context['chat_id'], text=f'Updates on group {group_name}')


def subscribe_on_updates(update: Update, context: CallbackContext) -> None:
    def get_job_name(chat_id, group_name):
        return f'SUBSCRIBE_SCHEDULE_UPDATES_{chat_id}_{group_name}'
    chat_id = update.message.chat_id
    logging.info('--> Requested subscribe on update with args %s by chat_id %s', context.args, chat_id)
    if len(context.args) == 0:
        update.message.reply_text('Please select a group using one letter')
        return
    group_name = context.args[0].upper()
    if not is_group_name(group_name):
        update.message.reply_text('Please select a proper group using one letter')
        return
    old_group_name = context.user_data['group_name']
    context.user_data['group_name'] = group_name
    job_removed = remove_job_if_exists(get_job_name(chat_id, old_group_name), context)
    context.job_queue.run_repeating(get_schedule_updates,
                                    interval=timedelta(seconds=20),
                                    context={'chat_id': chat_id,
                                             'group_name': group_name
                                             },
                                    name=get_job_name(chat_id, group_name))
    logging.info('<-- Subscribed chat_id %s for group %s', update.message.chat_id, group_name)
    update.message.reply_text(f'Successfully subscribed for updates of schedule in group {group_name}.\n'
                              'You will be notified when new schedule appears.')
