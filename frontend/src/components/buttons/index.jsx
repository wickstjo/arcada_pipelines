import './styles.scss'
import { ReactComponent as Lock } from './icons/lock.svg'
import { ReactComponent as Plus } from './icons/plus.svg'

function Buttons({ items }) {

    // MAP LABELS TO SVG ICONS FOR DYNAMIC RENDERING
    const icon_mapping = {
        lock: Lock,
        plus: Plus
    }

    return (
        <div className={ 'button_row' }>
            { items.map(item => {

                // SELECT THE CORRECT ICON
                const Icon = icon_mapping[item.icon]

                return (
                    <div className={ 'shadow' } onClick={ item.action } key={ 'button/' + item.label }>
                        <div className={ 'icon' }><Icon /></div>
                        <div className={ 'label' }>{ item.label }</div>
                    </div>
                )
            })}
        </div>
    )
}

export default Buttons