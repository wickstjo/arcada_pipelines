import { configureStore } from '@reduxjs/toolkit'
import { Provider } from 'react-redux'

// CREATE CUSTOM REDUCERS
import { reducer as misc } from './misc'

// MAKE THEM USABLE THROUGH THE GLOBAL STATE
const store = configureStore({
    reducer: {
        misc,
    }
})

const Component = ({ children }) => { return (
    <Provider store={ store }>
        { children }
    </Provider>
)}

export default Component