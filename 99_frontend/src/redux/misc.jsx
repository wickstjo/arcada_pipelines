import { createSlice } from '@reduxjs/toolkit'

// DEFINE THE INITIAL STATE
const init_state = {
    foo: 'bar'
}

// STATE ACTIONS
const actions = {

    update(state, action) {
        return {
            ...state,
            foo: action.value
        }
    },

}

// EXPORT SLICE REDUER
const reducer = createSlice({
    name: 'misc',
    initialState: init_state,
    reducers: actions,
}).reducer

export {
    reducer
}