#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import run_task
from utils import configure_logging

configure_logging()

async def test():
    task = """What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper "Can Hiccup Supply Enough Fish to Maintain a Dragon's Diet?" """
    final_answer, research_output = await run_task(task)
    print(f'Final Answer: {final_answer}')
    if final_answer and any(phrase in final_answer.lower() for phrase in ['cannot provide', 'unable to access', 'please provide', 'please upload']):
        print('❌ EARLY_TERMINATION: Agent gave up too early')
    else:
        print('✅ Agent handled appropriately')

asyncio.run(test())