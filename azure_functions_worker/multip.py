from typing import Callable, Dict, Any
import multiprocessing as mp
import logging


def multip_func_wrapper(func: Callable, func_kwargs: Dict[str, Any], func_ret: Dict[str, str]):
    result = func(**func_kwargs)
    func_ret['result'] = result


class Multip:
    def __init__(self, max_workers: int):
        self._mp_manager: mp.Manager = mp.Manager()
        self._max_workers = max_workers
        self._mp_queue: mp.queue = mp.Queue(65536)

    def register(self, func: Callable, func_kwargs: Dict[str, Any]):
        # kwargs can't pickle mappingproxy objects
        return_dict = self._mp_manager.dict()
        p: mp.Process = mp.Process(target=multip_func_wrapper, kwargs={
            'func': func,
            'func_kwargs': func_kwargs,
            'func_ret': return_dict
        })
        p.start()
        p.join()
        return return_dict['result']
