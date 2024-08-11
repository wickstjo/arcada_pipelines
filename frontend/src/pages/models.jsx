import { useEffect } from 'react'
import { useDispatch } from 'react-redux'

function Models() {

    // REDUX DISPATCHER
    const dispatch = useDispatch()

    // ON LOAD..
    useEffect(() => {
        dispatch({
            type: 'menu/update',
            category: 'Models'
        })
    })
    
    return (
        <div>Models page</div>
    )
}

export default Models