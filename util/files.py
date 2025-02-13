import json
import asyncio
from collections import defaultdict

import aiofiles


file_locks = defaultdict(asyncio.Lock)


async def load_file(file_path: str):
    lock = file_locks[file_path]
    async with lock:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            content = await file.read()
            return json.loads(content)

async def save_file(file_path: str, data):
    lock = file_locks[file_path]
    async with lock:
        async with aiofiles.open(file_path, mode='w', encoding='utf-8') as file:
            content = json.dumps(data, indent=2)
            await file.write(content)
