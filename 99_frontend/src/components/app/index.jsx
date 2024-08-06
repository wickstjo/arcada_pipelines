import './styles.scss';
import { Fragment } from 'react';
import { useSelector } from 'react-redux'

import Menu from '../menu'
import Prompt from '../prompt'
import useKeyboard from '../../hooks/keyboard_events'

function App() {
    
    // FETCH THE PROMPT STATE TO SMOOTHEN TRANSITIONS
    const prompt_state = useSelector(state => state.prompt)

    // REGISTER KEYBOARD LISTENER FOR SHORTCUTS
    const _ = useKeyboard()

    return (
        <Fragment>
            <div className={ 'main' } id={ prompt_state.window !== null ? 'blurred' : null }>
                <Menu />
            </div>
            <Prompt />
        </Fragment>
    )
}

export default App