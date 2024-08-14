import './styles.scss';
import { useSelector } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'

import useKeyboard from '../../hooks/keyboard_events'

import Menu from '../menu'
import Prompt from '../prompt'
import Notifications from '../notifications'
import Pages from '../../pages'

function App() {
    
    // FETCH THE PROMPT STATE TO SMOOTHEN TRANSITIONS
    const prompt_state = useSelector(state => state.prompt)

    // REGISTER KEYBOARD LISTENER FOR ACTION SHORTCUTS
    useKeyboard()

    return (
        <BrowserRouter>
            <div className={ 'main' } id={ prompt_state.window !== null ? 'blurred' : null }>
                <Menu />
                <div className={ 'innerbody' }>
                    <Pages />
                </div>
            </div>
            <Prompt />
            <Notifications />
        </BrowserRouter>
    )
}

export default App