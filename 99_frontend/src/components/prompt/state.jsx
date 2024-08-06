import { createSlice } from '@reduxjs/toolkit'
import { valid_windows } from './window_selector'

// INIT STATE
const init_state = {
    window: null
}

// STATE ACTIONS
const actions = {

    // OPEN SPECIFIC PROMPT
    show (state, args) {

        // A VALID WINDOW ARG WAS PASSED, OPEN PROMPT
        if (valid_windows.includes(args.window)) {
            return {
                ...state,
                window: args.window
            }

        // OTHERWISE, DO NOTHING AND THROW ERROR
        } else { console.log('ERROR: INVALID PROMPT WINDOW TYPE (' + args.window + ')') }
    },

    // HIDE PROMPT
    hide () {
        return {
            window: null
        }
    }
}

// EXPORT SLICE REDUER
export default createSlice({
    name: 'prompt',
    initialState: init_state,
    reducers: actions,
}).reducer