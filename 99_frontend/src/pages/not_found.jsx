import { useEffect } from 'react'
import { useDispatch } from 'react-redux'

function NotFound() {

    // REDUX DISPATCHER
    const dispatch = useDispatch()

    // ON LOAD..
    useEffect(() => {
        dispatch({
            type: 'menu/update',
            category: null
        })
    })
    
    return (
        <div>Page not found!</div>
    )
}

export default NotFound