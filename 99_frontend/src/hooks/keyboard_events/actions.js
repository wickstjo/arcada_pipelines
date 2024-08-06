function actions(pressed_key, dispatch, redux_state) {

    // WHEN ESC IS PRESSED, CLOSE ANY OPEN PROMPT WINDOW
    if (pressed_key === 'escape' && redux_state.prompt.window !== null) {
        dispatch({ type: 'prompt/hide' })
    }
}

export default actions