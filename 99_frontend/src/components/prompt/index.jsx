import './styles.scss'
import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { WindowSelector } from './window_selector'

function Prompt() {

    // REDUX STATE
    const dispatch = useDispatch()
    const prompt_state = useSelector(state => state.prompt)

    // VISIBILITY STATE
    const [style, set_style] = useState({
        top: '-100%',
        opacity: '0'
    })

    // WHEN THE STATE CHANGES, EVALUATE VISIBILITY
    useEffect(() => {
        set_style({
            top: prompt_state.window !== null ? '0' : '-100%',
            opacity: prompt_state.window !== null ? '100' : '0',
        })
    }, [prompt_state.window])

    return (
        <div id={ 'prompt' } style={ style }>
            <WindowSelector prompt_state={ prompt_state } />
            <span
                id={ 'close' }
                onClick={() => {
                    dispatch({ type: 'prompt/hide' })
                }}
            />
        </div>
    )
}

export default Prompt