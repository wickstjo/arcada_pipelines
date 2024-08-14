import './styles.scss'
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
        <div className={ 'error_page' }>
            <div className={ 'border' }>
                <div className={ 'msg' }>PAGE NOT FOUND</div>
            </div>
        </div>
    )
}

export default NotFound