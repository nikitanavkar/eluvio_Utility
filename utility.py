#!/usr/bin/env python
# coding: utf-8
import random, string
import sys
import os
import json
import asyncio
import aiohttp
import nest_asyncio
import base64

def generate_ids(n):
    inp_file = open("./ids.txt", "w")
    for i in range(n):
        id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))
        inp_file.write(id + "\n")

generate_ids(300)

conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
nest_asyncio.apply()
MAX_REQUESTS = 5
base_url = "https://challenges.qluv.io/items/"
with open('./ids.txt') as f:
    ids = f.read().splitlines()
results = {}

async def get_data():
    semaphore = asyncio.Semaphore(MAX_REQUESTS)
    session = aiohttp.ClientSession(connector=conn)
    async def get(id):
        if id not in results:
            async with semaphore:
                url = base_url + id
                base64_bytes = base64.b64encode(bytes(id, 'utf-8'))
                headers = {"Content-Type": "application/json; charset=utf-8", "Authorization":base64_bytes.decode("ascii")}
                async with session.get(url, headers=headers, ssl=False) as response:
                    obj = await response.read()
                    results[id] = obj.decode("ascii")
    await asyncio.gather(*(get(id) for id in ids))
    await session.close()

def process_requests():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_data())
    conn.close()
    file = open("output.txt", "w")
    file.writelines(["%s\n" % res  for res in list(results.values())])

process_requests()




