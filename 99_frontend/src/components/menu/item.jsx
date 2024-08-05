function MenuItem({ item, last_category }) {

    // BLOCK ACTION OF CURRENTLY SELECTED MENU ITEM
    const protected_action = () => {
        if (item.label !== last_category) {
            item.action(item.label)
        }
    }

    return (
        <div className={ item.label == last_category ? 'selected' : 'item' } id={ item.icon } onClick={ protected_action }>
            { item.label }
        </div>
    )
}

export default MenuItem