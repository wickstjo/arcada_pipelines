import { configureStore } from '@reduxjs/toolkit'
import { Provider } from 'react-redux'

// CREATE CUSTOM REDUCERS
import menu_state from './components/menu/state'
import prompt_state from './components/prompt/state'

// MAKE THEM USABLE THROUGH THE GLOBAL STATE
const store = configureStore({
    reducer: {
        menu: menu_state,
        prompt: prompt_state,
    }
})

const Component = ({ children }) => { return (
    <Provider store={ store }>
        { children }
    </Provider>
)}

export default Component