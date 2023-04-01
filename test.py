import asyncio
from concurrent.futures import ProcessPoolExecutor


async def main():
    i = 0
    while True:
        print(f'Hello{str(i)}')
        await asyncio.sleep(1)
        i += 1

def schedule_periodic():
    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(executor, main)



if __name__ == '__main__':
    schedule_periodic()

