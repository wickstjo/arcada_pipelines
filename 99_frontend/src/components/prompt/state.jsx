import { createSlice } from '@reduxjs/toolkit'

// INIT STATE
const init_state = {
    window: null
}

// STATE ACTIONS
const actions = {

    // OPEN SPECIFIC PROMPT
    show (state, args) {
        return {
            ...state,
            window: args.window
        }
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