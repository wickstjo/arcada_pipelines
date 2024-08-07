import './styles.scss'
import { useDispatch } from 'react-redux'
import { Internal, External, Trigger } from './items'

function Menu() {

    // REDUX STATE
    const dispatch = useDispatch()

    return (
        <div className={ 'menu' }>
            <div className={ 'upper' } />
            <div className={ 'lower' }>
                <Internal
                    label={ 'Models' }
                    goto={ 'models' }
                    icon={ 'db' }
                />
                <Internal
                    label={ 'Actions' }
                    goto={ 'actions' }
                    icon={ 'list' }
                />
                <External
                    label={ 'Flink' }
                    goto={ 'https://en.wikipedia.org/wiki/Apache_Flink' }
                    icon={ 'network' }
                />
                <External
                    label={ 'Prometheus' }
                    goto={ 'https://en.wikipedia.org/wiki/Prometheus_(software)' }
                    icon={ 'chart' }
                />
                <Trigger
                    label={ 'Settings' }
                    icon={ 'cog' }
                    action={() => {
                        dispatch({
                            type: 'prompt/show',
                            window: 'settings' 
                        })
                    }}
                />
                <Trigger
                    label={ 'P' }
                    icon={ 'plus' }
                    action={() => {
                        dispatch({
                            type: 'notify/positive',
                            message: 'Query returned successfully' 
                        })
                    }}
                />
                <Trigger
                    label={ 'N' }
                    icon={ 'plus' }
                    action={() => {
                        dispatch({
                            type: 'notify/negative',
                            message: 'Something went wrong' 
                        })
                    }}
                />
            </div>
        </div>
    )
}

export default Menu