import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'

const Entry = ({ item }) => {

    // REDUX DISPATCH
    const dispatch = useDispatch()

    const [style, set_style] = useState({
        opacity: 0,
        right: '-100%'
    })

    // ON LOAD...
    useEffect(() => {

        // SLIDE NOTIFICATION IN
        set_style({
            opacity: 1,
            right: '0px'
        })

        // AFTER n SECONDS, DRAW THE MSG BACK
        setTimeout(() => {
            set_style({
                opacity: 0,
                right: '-100%'
            })

            // AFTER N SECONDS, REMOVE THE MSG COMPLETELY
            setTimeout(() => {
                dispatch({
                    type: 'notify/remove',
                    id: item.id,
                })
            }, 400)
        }, item.duration-400)
    }, [dispatch, item.duration, item.id])

    return (
        <div className={ 'entry' } style={ style }>
            <div className={ item.kind + '_border' }>
                <div className={ item.kind + '_bg' }>
                    { item.message }
                </div>
            </div>
        </div>
    )
}

export default Entry