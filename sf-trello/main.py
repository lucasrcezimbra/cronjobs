import itertools
import requests
from datetime import date
from decouple import config
from trello import TrelloClient

def main():
    alerts = {
        'Lisiane': {
            'email': 'lisiane@sprintfinal.com.br',
            'cards': []
        },
        'Renato': {
            'email': 'renato@sprintfinal.com.br',
            'cards': []
        },
    }

    client = TrelloClient(
        api_key=config('TRELLO_API_KEY'),
        api_secret=config('TRELLO_API_SECRET'),
        token=config('TRELLO_TOKEN'),
    )

    print('--- Getting boards ---')
    boards = client.list_boards()
    diario = [board for board in boards if board.name == 'DIÁRIO'][0]

    print('--- Getting lists ---')
    lists = diario.list_lists()
    used_lists_names = ('Para Fazer', 'Fazendo',)
    used_lists = [list for list in lists if list.name in used_lists_names]

    print('--- Getting cards ---')
    cards = [list.list_cards() for list in used_lists]
    cards = list(itertools.chain.from_iterable(cards))

    for key,value in alerts.items():
        value['cards'] = [card.name
                          for card in cards
                          if card.labels and card.labels[0].name == key]

    print('--- Sending e-mails ---')
    _send_email(alerts)

def _send_email(alerts):
    URL = config('URL')
    today = date.today().strftime("%d/%m/%Y")
    for name,values in alerts.items():
        if not values['cards']:
            continue
        data = {
            'recipient': values['email'],
            'replyto': 'lucas@sprintfinal.com.br',
            'email': 'lucas@sprintfinal.com.br',
            'subject': 'Tarefas {} {}'.format(name, today),
            'tarefas': ''.join('\n- {}'.format(card)
                               for card in values['cards'])
        }
        data['tarefas'] = data['tarefas'].encode('latin_1')
        print('--- Sending e-mail to {} ---'.format(values['email']))
        requests.post(URL, data=data)

if __name__ == '__main__':
    main()
