import './styles.scss'
import Item from './item'
import { useState } from 'react'

function Container() {

    // ALL MENU ITEMS
    const items = [
        {
            label: 'Code',
            icon: 'chart',
            action: 'foo',
        },
        {
            label: 'Issues',
            icon: 'network',
            action: 'foo',
        },
        {
            label: 'Pull Requests',
            icon: 'db',
            action: 'foo',
        },
        {
            label: 'Actions',
            icon: 'list',
            action: 'foo',
        },
        {
            label: 'Settings',
            icon: 'cog',
            action: 'foo',
        },
    ]

    // CURRENTLY SELECTED ITEM
    const [current_item, update_current] = useState(items[2].label)

    return (
        <div className={ 'menu' }>
            <div className={ 'upper' } />
            <div className={ 'lower' }>
                { items.map(item =>
                    <Item
                        item={ item }
                        current_item={ current_item}
                        select_item={ update_current }
                    />
                )}
            </div>
        </div>
    )
}

export default Container