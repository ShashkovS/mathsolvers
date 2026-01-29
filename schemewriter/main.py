import asyncio
import importlib
import os
import sys
import webbrowser
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import mathsolvers

PORT = 8179


def reload_module(module):
    """Рекурсивно реимпортирует модуль и все его подмодули."""
    module_name = module.__name__
    modules_to_reload = [name for name in sys.modules if name.startswith(module_name)]
    modules_to_reload.sort(key=lambda n: n.count('.'), reverse=True)
    for name in modules_to_reload:
        mod = sys.modules.get(name)
        if mod:
            try:
                importlib.reload(mod)
            except Exception as e:
                print(f'Ошибка при реимпорте модуля {name}: {e}')


async def full_reload(app):
    await asyncio.sleep(0.1)
    if app.need_reload:
        try:
            reload_module(mathsolvers)
        except Exception as e:
            print(f'Ошибка при реимпорте mathsolvers: {e}')
        app.need_reload = False
        for websocket in app.clients:
            app.loop.create_task(websocket.send_text('reload'))
    return 'full_reload_done'


class ReloadMathsolversHandler(FileSystemEventHandler):
    def __init__(self, loop, app, *args, **kwargs):
        self._loop = loop
        self._app = app
        super().__init__(*args, **kwargs)

    def on_any_event(self, event):
        if event.event_type in ['modified', 'created', 'deleted'] and event.src_path.endswith('.py'):
            app.need_reload = True
            self._loop.call_soon_threadsafe(self._schedule_reload)

    def _schedule_reload(self):
        future = asyncio.ensure_future(full_reload(self._app), loop=self._loop)
        future.add_done_callback(self._reload_done)

    def _reload_done(self, future):
        try:
            result = future.result()
        except Exception as e:
            print(f'Ошибка при выполнении full_reload: {e}')


def start_observer(app):
    # Здесь замыкаем app внутрь класса
    loop = asyncio.get_event_loop()
    event_handler = ReloadMathsolversHandler(loop, app)
    observer = Observer()
    path = os.path.abspath('../src/mathsolvers')
    observer.schedule(event_handler, path=path, recursive=True)
    print(f"Следим за папкой '{path}'")
    observer.start()
    return observer


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    app.loop = loop
    app.loop.create_task(open_browser())
    app.observer = start_observer(app)
    yield
    app.observer.stop()
    app.observer.join()


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')


class SolverRequest(BaseModel):
    expr: str


@app.post('/solver')
async def solver(data: SolverRequest) -> Any:
    try:
        expr = data.expr
    except KeyError as e:
        print(f'Error: {e}')
        raise HTTPException(status_code=406, detail='nodata')
    try:
        sol_json = mathsolvers.solver(expr)
    except Exception as e:
        sol_json = {'error': str(e)}
    return JSONResponse(sol_json)


app.clients = set()
reload_done = False


@app.websocket('/ws/reload')
async def websocket_reload(websocket: WebSocket):
    global reload_done
    await websocket.accept()
    app.clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f'WebSocket error: {e}')
    finally:
        app.clients.remove(websocket)


async def open_browser():
    await asyncio.sleep(1)
    webbrowser.open(f'http://127.0.0.1:{PORT}/static/schemes.html?allfin=1&showtask=1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=PORT,
        reload=False,
    )
