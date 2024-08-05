import './styles.scss'
import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import FooWindow from './foo_window'

function Prompt() {

    // REDUX STATE
    const dispatch = useDispatch()
    const prompt_state = useSelector(state => state.prompt)

    // VISIBILITY STATE
    const [style, set_style] = useState({
        display: 'none',
    })

    // VALID PROMPT WINDOWS
    const valid_windows = {
        'foo': FooWindow,
    }

    // WHEN THE STATE CHANGES, EVALUATE VISIBILITY
    useEffect(() => {
        set_style({
            display: prompt_state.window !== null ? 'flex' : 'none',
        })
    }, [prompt_state.window])

    // IF PROMPT STATE IS NULL, RENDER NOTHING
    if (prompt_state.window === null) return null

    // IF A WHITELISTED WINDOW WAS DEFINED, RENDER IT
    if (prompt_state.window in valid_windows) {

        // FIRST, SELECT THE WINDOW COMPONENT
        const Window = valid_windows[prompt_state.window]

        return (
            <div id={ 'prompt' } style={ style }>
                <Window prompt_args={ prompt_state } />
                <span
                    id={ 'close' }
                    onClick={() => {
                        dispatch({ type: 'prompt/hide' })
                    }}
                />
            </div>
        )
    }

    // OTHERWISE, THROW ERROR FOR UNKNOWN INPUT
    console.log('UNKNOWN PROMPT WINDOW TYPE')
    return null
}

export default Prompt