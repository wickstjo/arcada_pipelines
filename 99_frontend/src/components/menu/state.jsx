import { createSlice } from '@reduxjs/toolkit'

// DEFINE THE INITIAL STATE
const init_state = {
    last_category: 'Actions'
}

// STATE ACTIONS
const actions = {

    update(state, args) {
        return {
            ...state,
            last_category: args.category
        }
    },

}

// EXPORT SLICE REDUER
export default createSlice({
    name: 'menu',
    initialState: init_state,
    reducers: actions,
}).reducer