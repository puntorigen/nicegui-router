from nicegui import ui
from typing import Callable
import sys, uuid, asyncio

refreshable_func_key = '_refreshable_func'

def use_state(default):
    for i in range(10):
        frame = sys._getframe(i)
        locals_ = frame.f_locals
        # print('Frame', frame, locals_)
        if '_context_state_' in locals_:
            state = locals_['_context_state_']
            #print('State!', state)
            refreshable_func = state.get(refreshable_func_key)
            break
    #print('Resolved', state, refreshable_func)
    key = state['__idx']
    ret = state.setdefault(key, default)
    state['__idx'] += 1
    def set_value(value):
        #print('Call Set Value', value, state, refreshable_func)
        state.update({key: value})
        refreshable_func.refresh()
    return ret, set_value


def component(func: Callable):
    if asyncio.iscoroutinefunction(func):
        async def __refresh_wrapper__(*args, **kwargs):
            def _co():
                _context_state_ = {'_id': uuid.uuid4()}
                async def __state_wrapper__(*args, **kwargs):
                    nonlocal _context_state_
                    try:
                        _context_state_['__idx'] = 0
                        ret = await func(*args, **kwargs)
                    finally:
                        _context_state_['__idx'] = 0
                    return ret
                return __state_wrapper__, _context_state_
            f, state = _co()
            _refreshable_func = ui.refreshable(f)
            state[refreshable_func_key] = _refreshable_func
            return await _refreshable_func(*args, **kwargs)
        return __refresh_wrapper__
    else:
        def __refresh_wrapper__(*args, **kwargs):
            def _co():
                _context_state_ = {'_id': uuid.uuid4()}
                def __state_wrapper__(*args, **kwargs):
                    nonlocal _context_state_
                    try:
                        _context_state_['__idx'] = 0
                        ret = func(*args, **kwargs)
                    finally:
                        _context_state_['__idx'] = 0
                    return ret
                return __state_wrapper__, _context_state_
            f, state = _co()
            _refreshable_func = ui.refreshable(f)
            state[refreshable_func_key] = _refreshable_func
            return _refreshable_func(*args, **kwargs)
        return __refresh_wrapper__




code = '''
```python
@component
def comp(title: str):
    value, set_value = use_state(0)
    msg, set_msg = use_state('Another State')
    ui.label(title + str(value))
    ui.button('Increment').on('click', lambda: set_value(value + 1))
    ui.button(msg).on('click', lambda e: set_msg('Clicked' + str(value)))


with ui.row().classes('w-full'):
    with ui.column().classes():
        ui.markdown(code)
    ui.splitter(horizontal=False).classes('w-10')
    with ui.column().classes('w-1/2'):
        comp('Component 1: ')
        ui.separator()
        comp('Component 2: ')


ui.run(title='Component Demo', host='127.0.0.1')
    ```

'''

