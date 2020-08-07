import pandas as pd
from os import path


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def log(fn, epoch, epoch_steps, total_steps, total_run_time, epsilon, verbose=True):

        if verbose:
            print(f'episode: {epoch}, #steps: {epoch_steps}, e: {epsilon}, total_steps: {total_steps}, total run time: {total_run_time}')

        data = [epoch, epoch_steps, total_steps, total_run_time, epsilon]

        if path.exists(f'log/{fn}'):
            pd.DataFrame(data).T.to_csv(f'log/{fn}', index=False, header=False, mode='a')

        else:
            pd.DataFrame(data, index=['epoch', 'epoch_steps', 'tot_steps', 'tot_run_time', 'epsilon']).T.to_csv(f'log/{fn}', index=False)

