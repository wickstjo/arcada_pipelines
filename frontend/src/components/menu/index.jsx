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
                    icon={ 'list' }
                />
                <Internal
                    label={ 'Kafka' }
                    goto={ 'kafka' }
                    icon={ 'db' }
                />
                <Internal
                    label={ 'Cassandra' }
                    goto={ 'cassandra' }
                    icon={ 'db' }
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
            </div>
        </div>
    )
}

export default Menu