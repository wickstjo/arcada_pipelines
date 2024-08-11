import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux'
import actions from './actions'

function useKeyboard() {

    // REDUX STATE
    const dispatch = useDispatch()
    const prompt = useSelector(state => state.prompt)

    // PERFORM ACTIONS WHEN SPECIFIC KEY EVENTS ARE TRIGGERED
    const handle_event = (event) => {

        // SANITIZE THE KEY TO AVOID CAPITALIZATION ISSUES
        const sanitized_key = event.key.toLowerCase()

        // PERFORM THE ACTION WHEN NECESSARY
        actions(sanitized_key, dispatch, {
            prompt
        })
    }
    
    // ON LOAD, CREATE THE KEYBOARD LISTENER
    useEffect(() => {
        document.addEventListener('keyup', handle_event);

        // ON UNLOAD, REMOVE IT
        return () => {
            document.removeEventListener('keyup', handle_event);
        }
    }, [prompt])

    return null
}

export default useKeyboard