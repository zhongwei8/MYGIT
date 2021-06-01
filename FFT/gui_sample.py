import PySimpleGUI as sg


def pop_list_boxes(items: list, location=(400, 300)):
    choice = None
    location = (400, 300)
    layout = [[
        sg.Listbox(values=items,
                   default_values=[0],
                   size=(20, 12),
                   key='Selected-delay',
                   enable_events=True)
    ],
              [
                  sg.Button('Submit(Enter)', key='btn_submit'),
                  sg.Button('Cancel(Esc/BackSpace)', key='btn_cancel')
              ]]
    window = sg.Window('choice', layout=layout, location=location)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event in {'btn_submit', 'Return:36'}:
            choice = values['Selected-delay'][0]
            break

    print(f'choice = {choice}')
    return choice


if __name__ == '__main__':
    items = [1, 2, 3, 4]
    pop_list_boxes(items)
