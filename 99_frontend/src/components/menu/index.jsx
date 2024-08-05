import './styles.scss'
import { useDispatch, useSelector } from 'react-redux'
import Item from './item'

function Menu() {

    // REDUX STATE
    const dispatch = useDispatch()
    const menu_state = useSelector(state => state.menu)

    // TEMP ACTION TRIGGER FOR MENU ITEMS
    const trigger = (label) => {
        dispatch({
            type: 'menu/update',
            category: label
        })
        dispatch({
            type: 'prompt/show',
            window: 'foo' 
        })
    }

    // ALL MENU ITEMS
    const items = [
        {
            label: 'Data',
            icon: 'file',
            action: trigger,
        },
        {
            label: 'Pipelines',
            icon: 'network',
            action: trigger,
        },
        {
            label: 'Actions',
            icon: 'list',
            action: trigger,
        },
        {
            label: 'Models',
            icon: 'db',
            action: trigger,
        },
        {
            label: 'Prometheus',
            icon: 'chart',
            action: trigger,
        },
        {
            label: 'Settings',
            icon: 'cog',
            action: trigger,
        },
    ]

    return (
        <div className={ 'menu' }>
            <div className={ 'upper' } />
            <div className={ 'lower' }>
                { items.map(item =>
                    <Item
                        item={ item }
                        last_category={ menu_state.last_category }
                        key={ item.label }
                    />
                )}
            </div>
        </div>
    )
}

export default Menu