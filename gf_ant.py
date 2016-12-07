# -*- coding: utf-8 -*-
import email
import email.header
import imaplib
import json
import time
import util
import easytrader
from datetime import datetime
from easytrader import helpers
from log import logger

config = {}


def parse(content):
    index1 = content.find("Hold1") - 2
    index2 = content.find("Total_profit_rate") - 2
    if index1 > 0:
        working = json.loads(content[0:index1])
        position = json.loads(content[index1:index2])
        buy_list = []
        for code in working['buy']:
            for tick in position:
                if position[tick]['code'] == code:
                    entity = position[tick]
                    buy_list.append(entity)
                    break

        working['buy'] = buy_list
        return working
    else:
        return json.loads(content[0:index2])


def mail():
    content = None
    conn = imaplib.IMAP4(config['mail_host'])
    conn.login(config['mail_user'], config['mail_pass'])
    conn.select()
    typ, data = conn.search(None, 'ALL')
    if typ != 'OK':
        logger.warn("No messages found!")
        return

    # typ, data = conn.search(None, '(FROM "ants2016")')
    for num in data[0].split():
        # typ, data = conn.fetch(num, '(RFC822)')
        typ, data = conn.fetch(num, '(RFC822)')
        if typ != 'OK':
            logger.warn("ERROR getting message", num)
            return
        msg = email.message_from_bytes(data[0][1])
        message_id = msg.get('Message-ID')
        logger.info(message_id)
        fr = email.utils.parseaddr(msg['From'])[1]
        if fr != 'ants2016@vip.163.com':
            continue
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        if not subject.startswith(config['group']):
            continue
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
            local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            if not util.is_today(local_date):
                continue
        else:
            logger.warn('can not get date tuple')
            continue
        with open(config['mail_db'], 'r') as f1:
            old_id = (f1.read()).format()
            if old_id == message_id:
                logger.info('mail is handled')
                content = '{"date": "", "sell": [], "buy": []}{"Total_profit_rate": "0%"}'
                break
            else:
                with open(config['mail_db'], 'w') as f2:
                    f2.write(message_id)

        for part in msg.walk():
            content = part.get_payload(decode=True).decode()
            content = content[0:content.find("\n")]
    conn.close()
    conn.logout()
    if content is None:
        return None
    else:
        return parse(content)


def read_config(path):
    try:
        global config
        config = helpers.file2dict(path)
    except ValueError:
        logger.error('配置文件格式有误，请勿使用记事本编辑，推荐使用 notepad++ 或者 sublime text')


def balk():
    while True:
        if util.is_trade_date():
            if datetime.now().hour > 9:
                break
            elif datetime.now().minute > 26 and datetime.now().hour == 9:
                logger.info('is trade day ready')
                break
            else:
                time.sleep(20)
        else:
            logger.info('sleep 663 sec')
            time.sleep(663)


def main():
    data = None
    balk()
    read_config("ant.json")
    logger.info(config)
    user = easytrader.use('gf', debug=False)
    user.prepare('gf.json')
    while True:
        data = mail()
        # data = parse('{"date": "2016-11-09", "sell": ["000210.xhae"], "buy": []}{"Total_profit_rate": "63%"}')
        if data is None:
            time.sleep(30)
        else:
            break
        if datetime.now().minute > 35:
            content = '{"date": "", "sell": [], "buy": []}{"Total_profit_rate": "0%"}'
            data = parse(content)
            logger.info("time out to read mail server")
            break

    positions = user.get_position()
    logger.info(positions)
    logger.info(data)
    for sell_code in data['sell']:
        sell_code = sell_code[0:6].format()
        message = 'sell clear  code ' + sell_code
        logger.info(message)
        for position in positions['data']:
            stock_code = position['stock_code']
            if stock_code == sell_code:
                amount = position['enable_amount']
                last_price = position['last_price']
                # result = user.sell(sell_code, price=last_price, amount=amount)
                # logger.info(result)
                message = 'sell clear code = ' + sell_code + ' amount=' + amount + ' last price=' + last_price
                logger.info(message)
                break

    for buy_entity in data['buy']:
        buy_code = buy_entity['code']
        buy_code = buy_code[0:6].format()
        volume = buy_entity['Weight'] * config['balance'] / 100
        cost = buy_entity['Cost']
        # result = user.buy(buy_code, price=cost, volume=volume)
        # logger.info(result)
        message = 'buy  code=' + buy_code + ' balance=' + str(volume) + ' last price=' + str(cost)
        logger.info(message)
    logger.info("ant working ending")


if __name__ == '__main__':
    main()
