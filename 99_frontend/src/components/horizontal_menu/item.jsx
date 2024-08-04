function Container({ item, current_item, select_item }) { return (
    <div className={ item.label == current_item ? 'selected' : 'item' } id={ item.icon } onClick={ () => select_item(item.label) }>
        { item.label }
    </div>
)}

export default Container