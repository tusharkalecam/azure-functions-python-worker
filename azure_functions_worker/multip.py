from typing import Callable, Dict, Any
from asyncio import Semaphore, AbstractEventLoop, sleep, new_event_loop
import multiprocessing as mp
from threading import BoundedSemaphore as BoundedSemaphore_
from multiprocessing.pool import Pool as Pool_
from multiprocessing.queues import Queue as Queue_
import logging


def multip_func_wrapper(
    func: Callable,
    func_kwargs: Dict[str, Any],
    func_ret: Dict[str, str]
):
    result = func(**func_kwargs)
    func_ret['result'] = result


def multip_func_wrapper2(
    invocation_id: str,
    is_async: bool,
    func: Callable,
    func_kwargs: Dict[str, Any],
    dict_ret: Dict[str, Any]
):
    if is_async is False:
        result = func(**func_kwargs)
    else:
        loop: AbstractEventLoop = new_event_loop()
        result = loop.run_until_complete(func(**func_kwargs))

    dict_ret[invocation_id] = result


class Multip:
    def __init__(self, max_workers: int):
        self._mp_manager: mp.Manager = mp.Manager()
        self._mp_cores: int = mp.cpu_count()
        self._mp_pool: Pool_ = mp.Pool(max_workers)
        self._mp_semaphore: Semaphore = Semaphore(self._mp_cores * 2 + 1)
        self._mp_result: Dict[str, Any] = {}
        self._mp_queue: Queue_ = mp.Queue()
        self._mp_dict = self._mp_manager.dict()
        # self._mp_awaiting: Dict[str, AsyncResult] = {}

    def register1(self, func: Callable, func_kwargs: Dict[str, Any]):
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

    async def register2(self,
                        invocation_id: str,
                        is_async: bool,
                        func: Callable,
                        func_kwargs: Dict[str, Any],
                        successful_callback: Callable):

        p: mp.Process = mp.Process(target=multip_func_wrapper2, kwargs={
            'invocation_id': invocation_id,
            'is_async': is_async,
            'func': func,
            'func_kwargs': func_kwargs,
            'dict_ret': self._mp_dict
        })

        await self._mp_semaphore.acquire()
        try:
            p.start()
            p.join()
        finally:
            p.terminate()
            self._mp_semaphore.release()

        result = self._mp_dict[invocation_id]
        del self._mp_dict[invocation_id]

        # logging.warning(f'CORE COUNTS : {self._mp_cores}')
        await successful_callback(result)
