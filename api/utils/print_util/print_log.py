import datetime


def PrintToTerminal(msg: str):
    """
    Terminal出力デバッグ用print()メソッド

    arg :
        msg : str -> 出力したいメッセージ

    ex output :
        [DG-MM Terminal Log: {出力日時}] MSG : {メッセージ}
    """
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msgf = '[DG-MM Terminal Log: {now}] MSG : {msg}'.format(**{
        'msg': msg,
        'now': now
    })
    print(msgf)
