import { Link } from 'react-router-dom'
import { useSelector } from 'react-redux'

// INTERNAL REACT LINKS
function Internal({ label, goto, icon }) {

    // REDUX STATE
    const current_category = useSelector(state => state.menu.last_category)

    // TOGGLE CLASS FOR CURRENTLY SELECTED CATEGORIES
    const dynamic_class = (label === current_category) ? 'selected' : 'item'

    // REMOVE HYPERLINKS FOR CURRENTLY SELECTED MENU ITEMS
    switch (label !== current_category) {

        // RENDER WITH LINK
        case true: { return (
            <Link to={ goto }>
                <div className={ dynamic_class } id={ icon }>
                    { label }
                </div>
            </Link>
        )}

        // OTHERWISE, RENDER WITHOUT THE LINK
        default: { return (
            <div className={ dynamic_class } id={ icon }>
                { label }
            </div>
        )}
    }
}

// EXTERNAL LINKS IN NEW TABS
function External({ label, goto, icon }) { return (
    <a href={ goto } target={ '_blank' } rel={ 'noopener noreferrer' }>
        <div className={ 'item' } id={ icon }>
            { label }
        </div>
    </a>
)}

// FUNCTION TRIGGERS
function Trigger({ label, action, icon }) { return (
    <div className={ 'item' } id={ icon } onClick={ action }>
        { label }
    </div>
)}

export {
    Internal,
    External,
    Trigger,
}