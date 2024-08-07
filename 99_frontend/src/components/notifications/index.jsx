import './styles.scss'
import { useSelector } from 'react-redux'
import Entry from './entry'

function Notifications() {

    // REDUX STATE
    const notifications = useSelector(state => state.notify)

    return (
        <div id={ 'notifications' }>
            { notifications.map(entry =>
                <Entry
                    key={ entry.id }
                    item={ entry }
                />
            )}
        </div>
    )
}

export default Notifications