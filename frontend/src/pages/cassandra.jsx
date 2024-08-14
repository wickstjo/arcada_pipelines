import { useEffect } from 'react'
import { useDispatch } from 'react-redux'

function Cassandra() {

    // REDUX DISPATCHER
    const dispatch = useDispatch()

    // ON LOAD..
    useEffect(() => {
        dispatch({
            type: 'menu/update',
            category: 'Cassandra'
        })
    })
    
    return (
        <div>Cassandra page</div>
    )
}

export default Cassandra