from asyncio import Queue
from typing import Dict

queues: Dict[int, Queue] = {}

async def put(chat_id: int, **kwargs) -> int:
    if chat_id not in queues:
        queues[chat_id] = Queue()
    await queues[chat_id].put({**kwargs})
    return queues[chat_id].qsize()

def get(chat_id: int) -> Dict[str, str]:
    if chat_id in queues:
        try:
            return queues[chat_id].get_nowait()
        except Queue.Empty:
            return None
    return None

def is_empty(chat_id: int) -> bool:
    return chat_id not in queues or queues[chat_id].empty()

def task_done(chat_id: int):
    if chat_id in queues:
        try:
            queues[chat_id].task_done()
        except ValueError:
            pass

def clear(chat_id: int):
    if chat_id in queues:
        queues[chat_id].queue.clear()
